"""Pruebas de rx-verificar-datos y rx-descargar-pesos: los dos comparan SHA-256 antes de confiar en un archivo.

No usan la red: la descarga se prueba con una URL file:// a una carpeta temporal.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rx_torax.data.checksums import read_manifest, sha256, verify, write_manifest
from rx_torax.inference import weights

ROOT = Path(__file__).resolve().parents[1]
MODEL_B_DATA = ROOT / 'configs' / 'nih_effusion_pa_modelo_b_v1.sha256'
PREPARED_FILES = {f'{kind}_{split}.npy' for kind in 'Xy' for split in ('train', 'val', 'test')} | \
                 {f'{split}.csv' for split in ('train', 'val', 'test')} | \
                 {'config.json', 'exclusiones.csv', 'labels.json', 'preprocessing.json', 'report.json'}


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


class DownloadWeightsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.release, self.models = root / 'release', root / 'models'
        self.release.mkdir()
        (self.release / 'modelo_x.pt').write_bytes(b'pesos del modelo x')
        self.source = self.release.as_uri()
        patcher = mock.patch.dict(weights.WEIGHTS, {'modelo_x': sha256(self.release / 'modelo_x.pt')}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.temp.cleanup()

    def test_download_verifies_and_does_not_repeat(self):
        target, downloaded = weights.download('modelo_x', self.models, self.source)
        self.assertTrue(downloaded)
        self.assertEqual(target.read_bytes(), b'pesos del modelo x')
        self.assertEqual(weights.download('modelo_x', self.models, self.source), (target, False))

    def test_corrupted_download_leaves_nothing(self):
        (self.release / 'modelo_x.pt').write_bytes(b'otra cosa')
        with self.assertRaises(ValueError):
            weights.download('modelo_x', self.models, self.source)
        self.assertEqual(list((self.models / 'modelo_x').iterdir()), [])

    def test_a_different_local_file_is_not_replaced(self):
        target = self.models / 'modelo_x' / 'modelo.pt'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'entrenado por otra persona')
        with self.assertRaises(ValueError):
            weights.download('modelo_x', self.models, self.source)
        self.assertEqual(target.read_bytes(), b'entrenado por otra persona')

    def test_unknown_model_is_rejected(self):
        with self.assertRaises(ValueError):
            weights.download('modelo_b_densenet121_v1', self.models, self.source)


class PublishedWeightsTests(unittest.TestCase):
    def test_local_weights_are_the_published_ones(self):
        present = {name: ROOT / 'models' / name / 'modelo.pt' for name in weights.WEIGHTS}
        present = {name: path for name, path in present.items() if path.is_file()}
        if not present:
            self.skipTest('Pesos de A, control y C no bajados (rx-descargar-pesos)')
        for name, path in present.items():
            with self.subTest(modelo=name):
                self.assertEqual(sha256(path), weights.WEIGHTS[name])


if __name__ == '__main__':
    unittest.main()
