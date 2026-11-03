"""Pruebas de la predicción sobre archivos de imagen, con datos sintéticos."""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from rx_torax.evaluation.evaluate import load_model, score
from rx_torax.inference.predict import predict
from rx_torax.preprocessing.images import transform
from rx_torax.training.train import DEFAULTS, train


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        data = self.root / 'datos'
        data.mkdir()
        rng = np.random.default_rng(0)
        self.paths = {}
        # Los arrays salen de PNG no cuadrados con transform, como en la preparación.
        for split, count in [('train', 16), ('val', 8)]:
            labels = np.array([1, 0] * (count // 2), dtype=np.int64)
            self.paths[split] = []
            for i, label in enumerate(labels):
                pixels = rng.random((80, 96)) * 0.2
                if label:
                    pixels[25:55, 30:66] += 0.7
                path = self.root / f'{split}_{i}.png'
                Image.fromarray((pixels * 255).astype(np.uint8)).save(path)
                self.paths[split].append(path)
            np.save(data / f'X_{split}.npy', np.stack([transform(path, 64) for path in self.paths[split]]))
            np.save(data / f'y_{split}.npy', labels)
        (data / 'preprocessing.json').write_text(
            json.dumps({'train_mean': 0.2, 'train_std': 0.2, 'image_size': 64}), encoding='utf-8')
        (data / 'labels.json').write_text(json.dumps({'target': 'Effusion'}), encoding='utf-8')
        self.model = self.root / 'modelo'
        train(DEFAULTS | {'data': str(data), 'output': str(self.model), 'pretrained': False, 'epochs': 2,
                          'batch_size': 4, 'device': 'cpu'})
        self.data = data

    def test_files_get_the_same_scores_as_the_prepared_arrays(self):
        rows, artifact = predict(self.model, self.paths['val'], 'cpu')
        _, model = load_model(self.model, 'cpu')
        expected = score(artifact, model, np.load(self.data / 'X_val.npy'), np.arange(8), 'cpu')
        self.assertEqual([row['image'] for row in rows], [str(path) for path in self.paths['val']])
        for row, value in zip(rows, expected):
            self.assertAlmostEqual(row['score'], value, places=6)
            self.assertEqual(row['predicted'], int(row['score'] >= artifact['threshold']))
        self.assertEqual(artifact['threshold'], torch.load(self.model / 'modelo.pt', weights_only=True)['threshold'])

    def test_bad_file_names_the_file(self):
        bad = self.root / 'informe.png'
        bad.write_text('no es una imagen', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'informe.png'):
            predict(self.model, [self.paths['val'][0], bad], 'cpu')

    def test_command_prints_and_writes_csv(self):
        output = self.root / 'predicciones.csv'
        result = subprocess.run(
            [sys.executable, '-m', 'rx_torax.inference.predict', '--modelo', str(self.model), '--salida', str(output),
             '--dispositivo', 'cpu', *map(str, self.paths['val'][:2])],
            capture_output=True, text=True, check=True)
        self.assertIn('val_0.png', result.stdout)
        self.assertIn('umbral', result.stdout)
        with output.open(newline='', encoding='utf-8') as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 2)


if __name__ == '__main__':
    unittest.main()
