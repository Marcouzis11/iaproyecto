"""Pruebas de métricas y del entrenamiento con datos sintéticos."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from rx_torax.evaluation.metrics import best_threshold, binary_metrics, roc_auc, trivial_baselines
from rx_torax.training.train import DEFAULTS, augment, load_config, repeat_positive_indices, train


class MetricsTests(unittest.TestCase):
    def test_auc_extremes_and_ties(self):
        self.assertEqual(roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)
        self.assertEqual(roc_auc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]), 0.0)
        self.assertEqual(roc_auc([0, 0, 1, 1], [0.5, 0.5, 0.5, 0.5]), 0.5)
        self.assertEqual(roc_auc([0, 1, 1], [0.5, 0.5, 0.9]), 0.75)

    def test_auc_needs_both_classes(self):
        with self.assertRaises(ValueError):
            roc_auc([1, 1], [0.1, 0.2])

    def test_binary_metrics_by_hand(self):
        result = binary_metrics([1, 1, 0, 0, 0], [0.9, 0.2, 0.8, 0.1, 0.3], 0.5)
        self.assertEqual((result['tp'], result['fn'], result['fp'], result['tn']), (1, 1, 1, 2))
        self.assertAlmostEqual(result['precision'], 0.5)
        self.assertAlmostEqual(result['recall'], 0.5)
        self.assertAlmostEqual(result['specificity'], 2 / 3)
        self.assertAlmostEqual(result['f1'], 0.5)

    def test_best_threshold_matches_exhaustive_search(self):
        rng = np.random.default_rng(0)
        labels = rng.integers(0, 2, 200)
        scores = np.round(np.clip(labels * 0.3 + rng.random(200) * 0.7, 0, 1), 2)
        chosen = binary_metrics(labels, scores, best_threshold(labels, scores))['f1']
        exhaustive = max(binary_metrics(labels, scores, t)['f1'] for t in np.unique(scores))
        self.assertAlmostEqual(chosen, exhaustive)

    def test_always_positive_baseline_at_40_percent(self):
        labels = np.array([1] * 40 + [0] * 60)
        baselines = trivial_baselines(labels)
        self.assertAlmostEqual(baselines['always_positive']['f1'], 2 * 0.4 / 1.4)
        self.assertEqual(baselines['always_negative']['f1'], 0.0)
        self.assertAlmostEqual(baselines['always_negative']['accuracy'], 0.6)


class TrainingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / 'data'
        self.data.mkdir()
        rng = np.random.default_rng(0)
        # A propósito no hay X_test ni y_test: si el entrenamiento los abriera, la prueba fallaría.
        for name, count in [('train', 16), ('val', 8)]:
            labels = np.array([1, 0] * (count // 2), dtype=np.int64)
            images = rng.random((count, 64, 64), dtype=np.float32) * 0.2
            images[labels == 1, 20:44, 20:44] += 0.7
            np.save(self.data / f'X_{name}.npy', images)
            np.save(self.data / f'y_{name}.npy', labels)
        (self.data / 'preprocessing.json').write_text(
            json.dumps({'train_mean': 0.2, 'train_std': 0.2, 'image_size': 64}), encoding='utf-8')
        (self.data / 'labels.json').write_text(json.dumps({'target': 'Effusion'}), encoding='utf-8')

    def config(self, name):
        return DEFAULTS | {'data': str(self.data), 'output': str(self.root / name), 'pretrained': False,
                           'epochs': 2, 'batch_size': 4, 'device': 'cpu'}

    def test_training_is_reproducible_and_never_needs_test(self):
        first = train(self.config('a'))
        second = train(self.config('b'))
        self.assertEqual(first['val']['threshold'], second['val']['threshold'])
        losses = [[row['val_loss'] for row in csv.DictReader(
            (self.root / name / 'historial.csv').read_text(encoding='utf-8').splitlines())] for name in 'ab']
        self.assertEqual(losses[0], losses[1])

    def test_artifact_has_what_inference_needs(self):
        report = train(self.config('a'))
        artifact = torch.load(self.root / 'a' / 'modelo.pt', weights_only=True)
        self.assertEqual(artifact['target'], 'Effusion')
        self.assertEqual(artifact['threshold'], report['val']['threshold'])
        self.assertEqual(artifact['epoch'], report['best_epoch'])
        self.assertEqual((artifact['train_mean'], artifact['train_std'], artifact['image_size']), (0.2, 0.2, 64))
        self.assertFalse((self.root / 'a.parcial').exists())

    def test_repeat_positives_only_changes_train_samples(self):
        labels = np.array([1, 0, 0, 1, 0])
        indices = np.array([0, 1, 3, 4])
        self.assertEqual(repeat_positive_indices(indices, labels, 1).tolist(), [0, 1, 3, 4])
        self.assertEqual(sorted(repeat_positive_indices(indices, labels, 3).tolist()), [0, 0, 0, 1, 3, 3, 3, 4])
        report = train(self.config('a') | {'repeat_positives': 3})
        self.assertEqual((report['train_images'], report['train_samples_per_epoch']), (16, 32))
        self.assertEqual(report['train_positive_fraction'], 0.75)
        self.assertEqual(report['val_images'], 8)

    def test_existing_output_is_refused(self):
        (self.root / 'a').mkdir()
        path = self.root / 'config.json'
        path.write_text(json.dumps({'data': str(self.data), 'output': str(self.root / 'a')}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'ya existe'):
            load_config(path)

    def test_output_override_replaces_the_json_output(self):
        (self.root / 'a').mkdir()
        path = self.root / 'config.json'
        path.write_text(json.dumps({'data': str(self.data), 'output': str(self.root / 'a')}), encoding='utf-8')
        self.assertEqual(load_config(path, self.root / 'b')['output'], str(self.root / 'b'))
        with self.assertRaisesRegex(ValueError, 'ya existe'):
            load_config(path, self.root / 'a')

    def test_unknown_config_key_is_refused(self):
        path = self.root / 'config.json'
        path.write_text(json.dumps({'data': 'd', 'output': str(self.root / 'x'), 'lr': 1}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'lr'):
            load_config(path)

    def test_augment_keeps_shape_range_and_varies_per_image(self):
        batch = torch.rand(4, 64, 64)
        batch[1] = batch[0]
        result = augment(batch, torch.Generator().manual_seed(0))
        self.assertEqual(result.shape, batch.shape)
        self.assertGreaterEqual(result.min().item(), 0.0)
        self.assertLessEqual(result.max().item(), 1.0)
        self.assertFalse(torch.equal(result[0], result[1]))


if __name__ == '__main__':
    unittest.main()
