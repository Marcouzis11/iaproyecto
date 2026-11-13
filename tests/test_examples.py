"""Pruebas del modelo versionado sobre las radiografías de ejemplo.

Usan el modelo B real (models/) y las cuatro radiografías de examples/, en CPU. Si cambia el
preprocesamiento, la carga del modelo o una dependencia, cambian los puntajes y la prueba falla.
"""

import unittest
from pathlib import Path

from rx_torax.inference.predict import DEFAULT_MODEL, predict

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples' / 'radiografias'

# Puntaje del modelo B en la evaluación de test y etiqueta real (1 = Effusion), según examples/radiografias/README.md.
DOCUMENTED = {
    '00022899_024.png': (0.940, 1),
    '00004526_023.png': (0.345, 1),
    '00000643_006.png': (0.575, 0),
    '00030344_002.png': (0.186, 0),
}
CELLS = {(1, 1): 'verdadero positivo', (1, 0): 'falso negativo', (0, 1): 'falso positivo', (0, 0): 'verdadero negativo'}


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows, cls.artifact = predict(ROOT / DEFAULT_MODEL, sorted(EXAMPLES.glob('*.png')), 'cpu')
        cls.rows = {Path(row['image']).name: row for row in rows}

    def test_examples_get_the_documented_scores(self):
        self.assertEqual(set(self.rows), set(DOCUMENTED))
        self.assertAlmostEqual(self.artifact['threshold'], 0.414, delta=0.001)
        for name, (expected, _) in DOCUMENTED.items():
            with self.subTest(imagen=name):
                # Coinciden hasta el tercer decimal: en CPU, MPS o CUDA pueden variar en el cuarto.
                self.assertAlmostEqual(self.rows[name]['score'], expected, delta=0.001)

    def test_one_example_per_cell_of_the_confusion_matrix(self):
        cells = {CELLS[label, self.rows[name]['predicted']] for name, (_, label) in DOCUMENTED.items()}
        self.assertEqual(cells, set(CELLS.values()))


if __name__ == '__main__':
    unittest.main()
