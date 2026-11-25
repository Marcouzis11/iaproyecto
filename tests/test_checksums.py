"""Pruebas de rx-verificar-datos y de los pesos versionados: los dos se comparan por SHA-256."""

import json
import tempfile
import unittest
from pathlib import Path

import torch

from rx_torax.data.checksums import read_manifest, sha256, verify, write_manifest

ROOT = Path(__file__).resolve().parents[1]
MODEL_B_DATA = ROOT / 'configs' / 'nih_effusion_pa_modelo_b_v1.sha256'
PREPARED_FILES = {f'{kind}_{split}.npy' for kind in 'Xy' for split in ('train', 'val', 'test')} | \
                 {f'{split}.csv' for split in ('train', 'val', 'test')} | \
                 {'config.json', 'exclusiones.csv', 'labels.json', 'preprocessing.json', 'report.json'}
# SHA-256 de cada modelo.pt versionado. Si un archivo cambia, deja de corresponder a sus reportes y predicciones.
WEIGHTS = {
    'modelo_a_densenet121_v1': '38a0f99199e53d4a72803259205ec98aa28a50b00d9e99a8f11b8cf29ab3039f',
    'modelo_b_densenet121_v1': 'e25a0b4a28cc9409c68e375d83f5104799db71cbd4bcaf9b6f4810b4a606b5e4',
    'modelo_control_v2_densenet121': '1c23c6aa85ee3c3f5e49fafa43a6211baf8b7c39794b4a896116f7345fdd3bf4',
    'modelo_c_v2_densenet121': '2aab1a55ade2692c72c9c1c50922765e2936b2e61981a9ed34e131dce6e8f01e',
}


class VerifyDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name) / 'preparados'
        self.folder.mkdir()
        for name, content in {'X_train.npy': b'arrays', 'train.csv': b'a,b\n1,2\n', '.DS_Store': b'x'}.items():
            (self.folder / name).write_bytes(content)
        self.manifest = Path(self.temp.name) / 'preparados.sha256'
        self.assertEqual(write_manifest(self.folder, self.manifest), 2)

    def tearDown(self):
        self.temp.cleanup()

    def test_identical_folder_passes_and_hidden_files_are_ignored(self):
        self.assertEqual(set(read_manifest(self.manifest)), {'X_train.npy', 'train.csv'})
        self.assertEqual(verify(self.folder, self.manifest), [])

    def test_changed_or_missing_files_are_reported(self):
        (self.folder / 'train.csv').write_bytes(b'a,b\n1,3\n')
        (self.folder / 'X_train.npy').unlink()
        self.assertEqual(sorted(verify(self.folder, self.manifest)), ['falta X_train.npy', 'train.csv tiene otro contenido'])

    def test_a_manifest_is_never_overwritten(self):
        with self.assertRaises(ValueError):
            write_manifest(self.folder, self.manifest)

    def test_model_b_data_manifest_lists_every_prepared_file(self):
        self.assertEqual(set(read_manifest(MODEL_B_DATA)), PREPARED_FILES)


class VersionedWeightsTests(unittest.TestCase):
    def test_each_weight_file_is_the_one_behind_its_reports(self):
        for name, digest in WEIGHTS.items():
            with self.subTest(modelo=name):
                folder = ROOT / 'models' / name
                self.assertEqual(sha256(folder / 'modelo.pt'), digest)
                artifact = torch.load(folder / 'modelo.pt', map_location='cpu', weights_only=True)
                training = json.loads((folder / 'report.json').read_text(encoding='utf-8'))
                validation = json.loads((folder / 'evaluacion_val' / 'report.json').read_text(encoding='utf-8'))
                self.assertEqual(artifact['epoch'], training['best_epoch'])
                self.assertEqual(artifact['threshold'], validation['threshold'])
                self.assertEqual((artifact['architecture'], artifact['image_size'], artifact['target']),
                                 ('densenet121', 224, 'Effusion'))


if __name__ == '__main__':
    unittest.main()
