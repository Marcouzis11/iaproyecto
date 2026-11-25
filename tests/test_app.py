"""Pruebas de rx-probar, la página local para probar el modelo.

Levantan el servidor en un puerto libre de 127.0.0.1, con el modelo B real en CPU, y le mandan las
radiografías de ejemplo como lo hace la página.
"""

import base64
import io
import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

from rx_torax.inference.app import Analizador, crear_servidor
from rx_torax.inference.predict import DEFAULT_MODEL

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples' / 'radiografias'
DOCUMENTED = {'00022899_024.png': 0.940, '00004526_023.png': 0.345, '00000643_006.png': 0.575, '00030344_002.png': 0.186}


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = crear_servidor(Analizador(ROOT / DEFAULT_MODEL, 'cpu'), puerto=0)
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def post(self, data):
        request = urllib.request.Request(self.url + '/api/predecir', data=data, method='POST',
                                         headers={'Content-Type': 'application/octet-stream'})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_page_and_model_info(self):
        with urllib.request.urlopen(self.url + '/', timeout=30) as response:
            self.assertEqual(response.status, 200)
            self.assertIn('Probar el modelo', response.read().decode('utf-8'))
        with urllib.request.urlopen(self.url + '/api/modelo', timeout=30) as response:
            info = json.loads(response.read())
        self.assertEqual(info['hallazgo'], 'Effusion')
        self.assertAlmostEqual(info['umbral'], 0.414, delta=0.001)

    def test_examples_get_the_same_scores_as_rx_predecir(self):
        for name, expected in DOCUMENTED.items():
            with self.subTest(imagen=name):
                status, result = self.post((EXAMPLES / name).read_bytes())
                self.assertEqual(status, 200)
                self.assertAlmostEqual(result['puntaje'], expected, delta=0.001)
                self.assertEqual(result['positivo'], result['puntaje'] >= result['umbral'])
                for key in ('entrada', 'mapa'):
                    prefix, encoded = result[key].split(',', 1)
                    self.assertEqual(prefix, 'data:image/png;base64')
                    self.assertEqual(Image.open(io.BytesIO(base64.b64decode(encoded))).size, (224, 224))

    def test_invalid_files_get_a_clear_error(self):
        status, result = self.post(b'esto no es una radiografia')
        self.assertEqual(status, 400)
        self.assertIn('PNG, JPEG o TIFF', result['error'])
        status, result = self.post(b'')
        self.assertEqual(status, 400)


if __name__ == '__main__':
    unittest.main()
