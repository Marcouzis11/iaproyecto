"""Pruebas del flujo completo y de las barreras contra fuga de datos."""

import csv
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

from rx_torax.data.metadata import audit, read_metadata
from rx_torax.demo import generate
from rx_torax.data.splits import select_balanced
from rx_torax.prepare import load_config, prepare
from rx_torax.preprocessing.images import read_image, transform


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = generate(self.root / 'raw')
        self.config = {'dataset': 'generic', 'target': 'target',
                       'metadata': str(self.raw / 'metadata.csv'), 'image_root': str(self.raw),
                       'output': str(self.root / 'processed'), 'image_size': 32,
                       'normalization': 'unit', 'seed': 42, 'ratios': [0.7, 0.15, 0.15]}

    def run_pipeline(self):
        path = self.root / 'config.json'
        path.write_text(json.dumps(self.config), encoding='utf-8')
        return prepare(path)

    def rows(self):
        with (self.raw / 'metadata.csv').open(newline='', encoding='utf-8') as stream:
            return list(csv.DictReader(stream))

    def write_rows(self, rows):
        with (self.raw / 'metadata.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_end_to_end_and_repeatability(self):
        out = self.run_pipeline()
        patients, total = [], 0
        for name in ('train', 'val', 'test'):
            with (out / f'{name}.csv').open(newline='', encoding='utf-8') as stream:
                rows = list(csv.DictReader(stream))
            x = np.load(out / f'X_{name}.npy', mmap_mode='r', allow_pickle=False)
            y = np.load(out / f'y_{name}.npy', allow_pickle=False)
            self.assertEqual(x.shape, (len(rows), 32, 32))
            self.assertEqual(x.dtype, np.float32)
            self.assertTrue(np.isfinite(x).all())
            self.assertGreaterEqual(float(x.min()), 0)
            self.assertLessEqual(float(x.max()), 1)
            np.testing.assert_array_equal(y, [int(r['target']) for r in rows])
            self.assertEqual(set(y), {0, 1})
            patients.append({r['patient_id'] for r in rows})
            total += len(rows)
            del x
        self.assertEqual(total, 120)
        self.assertFalse(patients[0] & patients[1] | patients[0] & patients[2] | patients[1] & patients[2])
        self.config['output'] = str(self.root / 'repeat')
        repeated = self.run_pipeline()
        for name in ('train', 'val', 'test'):
            self.assertEqual((out/f'{name}.csv').read_bytes(), (repeated/f'{name}.csv').read_bytes())
            self.assertEqual((out/f'X_{name}.npy').read_bytes(), (repeated/f'X_{name}.npy').read_bytes())
        with self.assertRaisesRegex(ValueError, 'ya existe'):
            self.run_pipeline()

    def test_bad_labels_files_and_duplicates_are_accounted(self):
        rows = self.rows()
        additions = [dict(rows[0], target='-1'), dict(rows[1], target=''),
                     dict(rows[2], image_path='images/missing.png'),
                     dict(rows[3], image_path='images/broken.png'), dict(rows[4])]
        (self.raw/'images/broken.png').write_bytes(b'not an image')
        self.write_rows(rows + additions)
        out = self.run_pipeline()
        report = json.loads((out/'report.json').read_text())
        for reason in ('uncertain_label', 'missing_label', 'missing_file', 'unreadable_image', 'duplicate_image'):
            self.assertEqual(report['exclusion_reasons'][reason], 1)
        self.assertEqual(report['source_rows'], report['accepted_images'] + report['excluded_rows'])

    def test_duplicate_across_patients_or_conflicting_labels_removes_both(self):
        rows = self.rows()
        self.write_rows(rows + [dict(rows[0], patient_id='other'), dict(rows[1], target='1')])
        records, excluded, _ = read_metadata(self.config)
        kept = audit(records, excluded)
        self.assertEqual(len(kept), 118)
        self.assertEqual(sum(r['reason'] == 'duplicate_across_patients' for r in excluded), 2)
        self.assertEqual(sum(r['reason'] == 'duplicate_conflicting_label' for r in excluded), 2)

    def test_explicit_patient_leakage_is_rejected(self):
        rows = self.rows()
        for i, row in enumerate(rows):
            row['split'] = ('train', 'val', 'test')[i % 3]
        self.write_rows(rows)
        with self.assertRaisesRegex(ValueError, 'Fuga'):
            self.run_pipeline()
        self.assertFalse((self.root/'processed').exists())
        self.assertTrue((self.root/'processed.audit.csv').exists())

    def test_train_statistics_do_not_depend_on_test(self):
        rows = self.rows()
        for row in rows:
            patient = int(row['patient_id'][1:])
            row['split'] = 'train' if patient < 40 else 'val' if patient < 50 else 'test'
        self.write_rows(rows)
        self.config['normalization'] = 'zscore'
        first = self.run_pipeline()
        stats = json.loads((first/'preprocessing.json').read_text())
        rng = np.random.default_rng(888)
        for row in rows:
            if row['split'] == 'test':
                Image.fromarray(rng.integers(200, 256, (48, 40), dtype=np.uint8)).save(self.raw/row['image_path'])
        self.config['output'] = str(self.root/'second')
        second = self.run_pipeline()
        self.assertEqual(stats, json.loads((second/'preprocessing.json').read_text()))
        a = np.load(first/'X_train.npy')
        b = np.load(second/'X_train.npy')
        np.testing.assert_array_equal(a, b)
        self.assertAlmostEqual(float(a.mean()), 0, places=5)
        self.assertAlmostEqual(float(a.std()), 1, places=5)

    def test_uint16_preserves_intensity(self):
        path = self.raw/'images/16bit.png'
        values = np.array([[0, 1000], [32768, 65535]], dtype=np.uint16)
        Image.fromarray(values).save(path)
        data, info = read_image(path)
        self.assertEqual(info['intensity_scale'], 65535)
        np.testing.assert_allclose(data, values.astype(np.float32)/65535)

    def test_resize_preserves_aspect_with_padding(self):
        path = self.raw/'images/wide.png'
        Image.fromarray(np.full((10, 20), 255, dtype=np.uint8)).save(path)
        result = transform(path, 32)
        self.assertTrue(np.all(result[:8] == 0))
        self.assertTrue(np.all(result[8:24] == 1))
        self.assertTrue(np.all(result[24:] == 0))

    def test_partial_explicit_splits_and_path_escape_rejected(self):
        rows = self.rows()
        for i, row in enumerate(rows):
            row['split'] = 'train' if i == 0 else ''
        self.write_rows(rows)
        with self.assertRaisesRegex(ValueError, 'split debe estar completa'):
            read_metadata(self.config)
        rows = [dict(image_path='../outside.png', patient_id='p', target='1')]
        self.write_rows(rows)
        records, excluded, _ = read_metadata(self.config)
        self.assertEqual(records, [])
        self.assertEqual(excluded[0]['reason'], 'path_outside_image_root')

    def test_chexpert_adapter_excludes_uncertainty(self):
        base = self.raw/'CheXpert-v1.0-small/train/patient00001/study1'
        base.mkdir(parents=True)
        Image.fromarray(np.arange(100, dtype=np.uint8).reshape(10, 10)).save(base/'view1.png')
        self.write_rows([{'Path': 'CheXpert-v1.0-small/train/patient00001/study1/view1.png',
                          'Frontal/Lateral': 'Frontal', 'Effusion': '1'},
                         {'Path': 'missing.png', 'Frontal/Lateral': 'Frontal', 'Effusion': '-1'}])
        self.config.update(dataset='chexpert', target='Effusion', frontal_only=True)
        records, excluded, _ = read_metadata(self.config)
        kept = audit(records, excluded)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]['patient_id'], 'patient00001')
        self.assertEqual(excluded[0]['reason'], 'uncertain_label')

    def test_nih_adapter_and_ambiguous_filename(self):
        original = self.rows()[0]['image_path']
        self.write_rows([{'Image Index': Path(original).name, 'Patient ID': '123',
                          'Finding Labels': 'Effusion|Atelectasis', 'View Position': 'PA'}])
        self.config.update(dataset='nih', target='Effusion', frontal_only=True)
        records, excluded, _ = read_metadata(self.config)
        self.assertEqual(len(audit(records, excluded)), 1)
        other = self.raw/'other'
        other.mkdir()
        (other/Path(original).name).write_bytes((self.raw/original).read_bytes())
        records, excluded, _ = read_metadata(self.config)
        self.assertFalse(records)
        self.assertEqual(excluded[0]['reason'], 'ambiguous_filename')

    def test_opaque_rgba_is_read_and_transparent_rgba_is_rejected(self):
        rgba = np.full((8, 8, 4), 255, dtype=np.uint8)
        rgba[..., :3] = 100
        Image.fromarray(rgba, 'RGBA').save(self.root/'opaca.png')
        pixels, info = read_image(self.root/'opaca.png')
        self.assertEqual(info['mode'], 'RGBA')
        self.assertTrue(np.allclose(pixels, 100/255))
        rgba[0, 0, 3] = 0
        Image.fromarray(rgba, 'RGBA').save(self.root/'transparente.png')
        with self.assertRaisesRegex(ValueError, 'transparencia'):
            read_image(self.root/'transparente.png')

    def test_nih_views_keeps_only_requested_view(self):
        rows = self.rows()[:2]
        self.write_rows([{'Image Index': Path(r['image_path']).name, 'Patient ID': r['patient_id'],
                          'Finding Labels': 'Pneumothorax', 'View Position': view}
                         for r, view in zip(rows, ['PA', 'AP'])])
        self.config.update(dataset='nih', target='Pneumothorax', frontal_only=True, views=['pa'])
        path = self.root/'config.json'
        path.write_text(json.dumps(self.config), encoding='utf-8')
        records, excluded, _ = read_metadata(load_config(path))
        self.assertEqual([Path(r['image_path']).name for r in records], [Path(rows[0]['image_path']).name])
        self.assertEqual(excluded[0]['reason'], 'excluded_view')

    def test_selection_keeps_positives_and_same_fraction_per_split(self):
        rows = []
        for p in range(600):
            for study in range(2):
                positive = (p // 3) % 8 == 0
                labels = 'Effusion' if positive else ('No Finding' if (p // 3) % 7 < 4 else 'Mass')
                rows.append({'image_path': f'p{p}_{study}.png', 'patient_id': f'p{p}', 'split': '',
                             'target': int(positive), 'target_original': labels, 'pixel_hash': f'{p}_{study}'})
        names = ('train', 'val', 'test')
        full = {name: [r for r in rows if int(r['patient_id'][1:]) % 3 == i] for i, name in enumerate(names)}
        config = {'seed': 42, 'selection': {'positive_fraction': 0.4, 'no_finding_share': 0.65,
                                            'max_negatives_per_patient': 1}}
        selected = select_balanced(full, config)
        self.assertEqual(selected, select_balanced(full, config))
        for name in names:
            chosen = selected[name]
            positives = [r for r in chosen if r['target'] == 1]
            self.assertEqual(len(positives), sum(r['target'] == 1 for r in full[name]))
            self.assertAlmostEqual(len(positives) / len(chosen), 0.4, places=2)
            negatives = [r for r in chosen if r['target'] == 0]
            self.assertEqual(len({r['patient_id'] for r in negatives}), len(negatives))
            self.assertAlmostEqual(sum(r['target_original'] == 'No Finding' for r in negatives) / len(negatives),
                                   0.65, places=1)

    def test_selection_cap_counts_all_negatives_of_a_patient(self):
        rows = [{'image_path': f'p{p}_{s}.png', 'patient_id': f'p{p}', 'target': 0,
                 'target_original': 'No Finding' if s < 2 else 'Mass'} for p in range(40) for s in range(4)]
        rows += [{'image_path': f'q{p}.png', 'patient_id': f'q{p}', 'target': 1, 'target_original': 'Effusion'}
                 for p in range(20)]
        config = {'seed': 42, 'selection': {'positive_fraction': 0.4, 'no_finding_share': 0.5,
                                            'max_negatives_per_patient': 2}}
        selected = select_balanced({'train': rows, 'val': rows, 'test': rows}, config)
        counts = Counter(r['patient_id'] for r in selected['train'] if r['target'] == 0)
        self.assertLessEqual(max(counts.values()), 2)

    def test_selection_stops_when_negatives_are_missing(self):
        rows = [{'image_path': f'p{i}.png', 'patient_id': f'p{i}', 'target': int(i < 8),
                 'target_original': 'Effusion' if i < 8 else 'No Finding'} for i in range(10)]
        config = {'seed': 42, 'selection': {'positive_fraction': 0.4, 'no_finding_share': 0.65,
                                            'max_negatives_per_patient': 3}}
        with self.assertRaisesRegex(ValueError, 'no alcanzan'):
            select_balanced({'train': rows, 'val': rows, 'test': rows}, config)

    def test_nih_official_test_is_preserved(self):
        rows = self.rows()
        self.write_rows([{'Image Index': Path(r['image_path']).name, 'Patient ID': r['patient_id'],
                          'Finding Labels': 'Effusion' if r['target'] else 'No Finding',
                          'View Position': 'PA'} for r in
                         [dict(r, target=int(r['target'])) for r in rows]])
        train = [Path(r['image_path']).name for r in rows if int(r['patient_id'][1:]) < 50]
        test = [Path(r['image_path']).name for r in rows if int(r['patient_id'][1:]) >= 50]
        (self.raw/'train_val_list.txt').write_text('\n'.join(train))
        (self.raw/'test_list.txt').write_text('\n'.join(test))
        self.config.update(dataset='nih', target='Effusion', frontal_only=True)
        out = self.run_pipeline()
        with (out/'test.csv').open(newline='', encoding='utf-8') as stream:
            exported = list(csv.DictReader(stream))
        self.assertEqual({Path(r['image_path']).name for r in exported}, set(test))
        report = json.loads((out/'report.json').read_text())
        self.assertEqual(report['split_method'], 'explicit_test_patient_validation_from_train')

    def test_insufficient_class_support_stops_export(self):
        rows = self.rows()
        for row in rows:
            row['target'] = '0'
        self.write_rows(rows)
        with self.assertRaisesRegex(ValueError, 'cada clase'):
            self.run_pipeline()
        self.assertFalse((self.root/'processed').exists())


if __name__ == '__main__':
    unittest.main()
