"""Pruebas de rx-recalcular sobre las predicciones versionadas de los cuatro modelos.

No usan NIH ni GPU: leen el puntaje, la etiqueta y el paciente de cada imagen evaluada y tienen que llegar
a los mismos números de los report.json y de las tablas del README.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from rx_torax.evaluation.evaluate import read_rows
from rx_torax.evaluation.recompute import recompute_all

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'models'
COLUMNS = {'array_index', 'image', 'patient_id', 'target', 'target_original', 'score', 'predicted'}


def by_name(results):
    return {(r['folder'].parent.name if r['kind'] == 'evaluación' else r['folder'].name, r['report']['split']): r
            for r in results}


class RecomputeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = by_name(recompute_all(MODELS))

    def test_every_versioned_result_is_reproduced(self):
        evaluations = [key for key, r in self.results.items() if r['kind'] == 'evaluación']
        comparisons = [key for key, r in self.results.items() if r['kind'] == 'comparación']
        self.assertEqual(len(evaluations), 7)
        self.assertEqual(len(comparisons), 3)
        for key, result in self.results.items():
            with self.subTest(resultado=key):
                self.assertEqual(result['mismatches'], [])

    def test_documented_numbers(self):
        def evaluation(model, split):
            recomputed = self.results[(model, split)]['recomputed']
            return recomputed['metrics'], recomputed['intervals_95']

        metrics, ranges = evaluation('modelo_b_densenet121_v1', 'test')
        self.assertEqual(round(metrics['f1'], 3), 0.744)
        self.assertEqual([round(value, 3) for value in ranges['f1']], [0.726, 0.761])
        self.assertEqual(round(metrics['auc'], 3), 0.869)
        self.assertEqual((metrics['tp'], metrics['fn'], metrics['fp'], metrics['tn']), (1634, 122, 1005, 1629))
        self.assertEqual(round(evaluation('modelo_a_densenet121_v1', 'val')[0]['f1'], 3), 0.795)
        self.assertEqual(round(evaluation('modelo_b_densenet121_v1', 'val')[0]['f1'], 3), 0.800)
        self.assertEqual(round(evaluation('modelo_control_v2_densenet121', 'test')[0]['f1'], 3), 0.775)
        self.assertEqual(round(evaluation('modelo_c_v2_densenet121', 'test')[0]['f1'], 3), 0.784)
        comparison = self.results[('comparacion_test_control_c', 'test')]['recomputed']
        low, high = comparison['intervals_95']['f1_diferencia']
        self.assertLess(low, 0)
        self.assertGreater(high, 0)
        self.assertEqual(comparison['metrics']['Control']['fp'] - comparison['metrics']['C']['fp'], 26)

    def test_predictions_publish_score_label_and_patient(self):
        paths = sorted(MODELS.glob('*/evaluacion_*/predicciones_*.csv'))
        self.assertEqual(len(paths), 7)
        for path in paths:
            with self.subTest(archivo=str(path.relative_to(ROOT))):
                rows = read_rows(path)
                self.assertEqual(set(rows[0]), COLUMNS)
                self.assertTrue(all(r['patient_id'] and r['image'].endswith('.png') for r in rows))
                self.assertTrue(all(0 <= float(r['score']) <= 1 for r in rows))
                self.assertEqual({r['target'] for r in rows}, {'0', '1'})
                self.assertAlmostEqual(sum(r['target'] == '1' for r in rows) / len(rows), 0.4, delta=0.01)

    def test_no_patient_is_in_validation_and_test(self):
        for model in ('modelo_b_densenet121_v1', 'modelo_c_v2_densenet121'):
            with self.subTest(modelo=model):
                patients = {split: {r['patient_id'] for r in read_rows(
                    MODELS / model / f'evaluacion_{split}' / f'predicciones_{split}.csv')} for split in ('val', 'test')}
                self.assertFalse(patients['val'] & patients['test'])

    def test_an_altered_report_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = MODELS / 'modelo_b_densenet121_v1' / 'evaluacion_test'
            copy = Path(folder) / 'models' / 'modelo_b_densenet121_v1' / 'evaluacion_test'
            copy.mkdir(parents=True)
            for name in ('report.json', 'predicciones_test.csv'):
                shutil.copy(source / name, copy / name)
            report = json.loads((copy / 'report.json').read_text(encoding='utf-8'))
            report['metrics']['f1'] += 0.01
            (copy / 'report.json').write_text(json.dumps(report), encoding='utf-8')
            (result,) = recompute_all(copy.parents[1])
            self.assertEqual([key for key, _ in result['mismatches']], ['metrics.f1'])


if __name__ == '__main__':
    unittest.main()
