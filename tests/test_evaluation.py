"""Pruebas de la evaluación final y de la comparación pareada, con datos sintéticos."""

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from rx_torax.evaluation.compare import compare
from rx_torax.evaluation.evaluate import bootstrap, evaluate
from rx_torax.evaluation.metrics import at_prevalence, binary_metrics, roc_auc, roc_curve
from rx_torax.training.train import DEFAULTS, train


class MetricsTests(unittest.TestCase):
    def test_roc_curve_area_matches_auc(self):
        rng = np.random.default_rng(1)
        labels = rng.integers(0, 2, 300)
        scores = np.round(labels * 0.3 + rng.random(300) * 0.7, 2)
        fpr, tpr = roc_curve(labels, scores)
        self.assertEqual((fpr[0], tpr[0], fpr[-1], tpr[-1]), (0.0, 0.0, 1.0, 1.0))
        self.assertAlmostEqual(float(np.trapezoid(tpr, fpr)), roc_auc(labels, scores))

    def test_at_prevalence_by_hand(self):
        result = at_prevalence(0.8, 0.9, 0.1)
        self.assertAlmostEqual(result['precision'], 0.08 / (0.08 + 0.09))
        self.assertAlmostEqual(result['f1'], 2 * result['precision'] * 0.8 / (result['precision'] + 0.8))

    def test_bootstrap_resamples_whole_patients(self):
        patients = np.array(['a', 'a', 'b', 'c', 'c', 'c', 'd'])
        labels = np.array([1, 1, 0, 1, 1, 0, 0])
        seen = bootstrap(labels, patients, lambda chosen: {'chosen': chosen}, 50, 0)
        sizes = {'a': 2, 'b': 1, 'c': 3, 'd': 1}
        for sample in seen:
            picked = patients[sample['chosen']]
            for patient, size in sizes.items():
                self.assertEqual((picked == patient).sum() % size, 0)
        again = bootstrap(labels, patients, lambda chosen: {'chosen': chosen}, 50, 0)
        self.assertTrue(all(np.array_equal(x['chosen'], y['chosen']) for x, y in zip(seen, again)))


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.make_data('datos', 0)

    def make_data(self, name, seed):
        data = self.root / name
        data.mkdir()
        rng = np.random.default_rng(seed)
        metadata = []
        for split, count in [('train', 16), ('val', 8), ('test', 12)]:
            labels = np.array([1, 0] * (count // 2), dtype=np.int64)
            images = rng.random((count, 64, 64), dtype=np.float32) * 0.2
            images[labels == 1, 20:44, 20:44] += 0.7
            np.save(data / f'X_{split}.npy', images)
            np.save(data / f'y_{split}.npy', labels)
            rows = [{'image_path': f'/raw/{split}_{i}.png', 'patient_id': f'{split}{i // 2}', 'target': int(label),
                     'target_original': ('Effusion' if i % 4 == 0 else 'Effusion|Mass') if label else
                     ('No Finding' if i % 4 == 1 else 'Mass')} for i, label in enumerate(labels)]
            with (data / f'{split}.csv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            metadata += [{'Image Index': f'{split}_{i}.png', 'Patient Age': 30 + 7 * i, 'Patient Sex': 'MF'[i % 2],
                          'Follow-up #': i} for i in range(count)]
        with (data / 'metadata.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(metadata[0]))
            writer.writeheader()
            writer.writerows(metadata)
        (data / 'config.json').write_text(json.dumps({'dataset': 'nih', 'metadata': str(data / 'metadata.csv')}),
                                          encoding='utf-8')
        (data / 'preprocessing.json').write_text(
            json.dumps({'train_mean': 0.2, 'train_std': 0.2, 'image_size': 64}), encoding='utf-8')
        (data / 'labels.json').write_text(json.dumps({'target': 'Effusion'}), encoding='utf-8')
        return data

    def model(self, name, data=None):
        train(DEFAULTS | {'data': str(data or self.data), 'output': str(self.root / name), 'pretrained': False,
                          'epochs': 2, 'batch_size': 4, 'device': 'cpu'})
        return self.root / name

    def test_test_uses_validation_threshold_and_runs_only_once(self):
        model = self.model('a')
        report = evaluate(model, 'test', device='cpu')
        artifact = torch.load(model / 'modelo.pt', weights_only=True)
        self.assertEqual(report['threshold'], artifact['threshold'])
        with (model / 'evaluacion_test' / 'predicciones_test.csv').open(newline='', encoding='utf-8') as stream:
            rows = list(csv.DictReader(stream))
        labels = np.array([int(r['target']) for r in rows])
        scores = np.array([float(r['score']) for r in rows])
        expected = binary_metrics(labels, scores, artifact['threshold'])
        self.assertEqual({k: report['metrics'][k] for k in expected}, expected)
        low, high = report['intervals_95']['auc']
        self.assertLessEqual(low, high)
        self.assertEqual(report['subgroups']['sexo_F']['images'], 6)
        self.assertEqual(report['subgroups']['positivos_sin_otros_hallazgos']['positives'], 3)
        for name in ('resultados.png', 'ejemplos.png', 'report.json'):
            self.assertTrue((model / 'evaluacion_test' / name).is_file())
        with self.assertRaisesRegex(ValueError, 'ya existe'):
            evaluate(model, 'test', device='cpu')

    def test_compare_is_paired_and_refuses_other_validation(self):
        model = self.model('a')
        copy = self.root / 'copia'
        shutil.copytree(model, copy)
        report = compare([model, copy], self.root / 'comparacion', ['A', 'A2'], device='cpu')
        self.assertEqual(report['differences']['auc_diferencia'], 0.0)
        self.assertEqual(report['intervals_95']['f1_diferencia'], [0.0, 0.0])
        self.assertEqual(report['disagreements'], 0)
        self.assertTrue((self.root / 'comparacion' / 'comparacion_val.png').is_file())
        other = self.model('b', self.make_data('otros', 1))
        with self.assertRaisesRegex(ValueError, 'mismo conjunto'):
            compare([model, other], self.root / 'otra', device='cpu')

    def test_compare_on_test_only_reads_saved_predictions(self):
        model = self.model('a')
        copy = self.root / 'copia'
        shutil.copytree(model, copy)
        with self.assertRaisesRegex(ValueError, 'primero hay que evaluar'):
            compare([model, copy], self.root / 'comparacion', device='cpu', split='test')
        evaluate(model, 'test', device='cpu')
        evaluate(copy, 'test', device='cpu')
        report = compare([model, copy], self.root / 'comparacion', ['A', 'A2'], split='test')
        self.assertEqual((report['split'], report['device']), ('test', 'None'))
        self.assertEqual(report['differences']['f1_diferencia'], 0.0)
        self.assertTrue((self.root / 'comparacion' / 'comparacion_test.png').is_file())


if __name__ == '__main__':
    unittest.main()
