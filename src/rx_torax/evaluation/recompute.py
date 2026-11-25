"""CLI: rx-recalcular. Rehace las métricas sin NIH, sin GPU y sin reentrenar.

Lee el puntaje, la etiqueta y el paciente de cada imagen evaluada (models/*/evaluacion_*/predicciones_*.csv),
recalcula métricas, intervalos y diferencias pareadas con el mismo código que rx-evaluar y rx-comparar,
y verifica que coincidan con los report.json versionados. Termina con código 1 si alguno no coincide.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from rx_torax.evaluation.compare import paired_differences
from rx_torax.evaluation.evaluate import metrics_with_intervals, read_rows, summary
from rx_torax.evaluation.metrics import binary_metrics

DEFAULT_MODELS = Path('models')
# Con los puntajes guardados los números salen idénticos; el margen solo cubre redondeos entre sistemas operativos.
TOLERANCE = 1e-9


def load_predictions(folder, split):
    """Índice, etiqueta, puntaje y paciente de cada imagen, en el orden del conjunto."""
    path = Path(folder) / f'predicciones_{split}.csv'
    if not path.is_file():
        raise ValueError(f'No existe {path}')
    rows = read_rows(path)
    index = np.array([int(r['array_index']) for r in rows])
    if not np.array_equal(index, np.arange(len(rows))):
        raise ValueError(f'{path}: las filas no están en el orden del conjunto')
    return {'labels': np.array([int(r['target']) for r in rows]),
            'scores': np.array([float(r['score']) for r in rows]),
            'patients': np.array([r['patient_id'] for r in rows]),
            'images': [r['image'] for r in rows]}


def read_report(folder):
    return json.loads((Path(folder) / 'report.json').read_text(encoding='utf-8'))


def recompute_evaluation(folder):
    """Lo que rx-evaluar guardó en metrics, intervals_95 y bootstrap.valid_rounds."""
    report = read_report(folder)
    data = load_predictions(folder, report['split'])
    metrics, ranges, valid_rounds = metrics_with_intervals(data['labels'], data['scores'], data['patients'],
                                                           report['threshold'])
    return report, {'metrics': metrics, 'intervals_95': ranges, 'bootstrap': {'valid_rounds': valid_rounds}}


def recompute_comparison(folder, root):
    """Lo que rx-comparar guardó, a partir de las predicciones de la evaluación de cada modelo."""
    report = read_report(folder)
    split = report['split']
    scored = {}
    for name, model in report['models'].items():
        evaluation = Path(root) / model / f'evaluacion_{split}'
        scored[name] = (load_predictions(evaluation, split), read_report(evaluation)['threshold'])
    (first, (a, t1)), (second, (b, t2)) = scored.items()
    if a['images'] != b['images'] or not np.array_equal(a['labels'], b['labels']) \
            or not np.array_equal(a['patients'], b['patients']):
        raise ValueError(f'{folder}: {first} y {second} no tienen las mismas imágenes; la comparación no es pareada')
    labels = a['labels']
    differences, ranges, better, valid_rounds = paired_differences(labels, a['patients'], (a['scores'], t1),
                                                                   (b['scores'], t2))
    metrics = {name: summary(labels, d['scores'], t) | binary_metrics(labels, d['scores'], t)
               for name, (d, t) in scored.items()}
    return report, {'metrics': metrics, 'differences': differences, 'intervals_95': ranges,
                    'probability_second_better': better, 'bootstrap': {'valid_rounds': valid_rounds}}


def mismatches(recomputed, stored, path=''):
    """Claves numéricas que no coinciden con lo guardado, con su diferencia."""
    found = []
    if isinstance(recomputed, dict):
        for key, value in recomputed.items():
            if key not in stored:
                found.append((f'{path}{key}', 'falta en report.json'))
            else:
                found += mismatches(value, stored[key], f'{path}{key}.')
    elif isinstance(recomputed, (list, tuple)):
        for position, (value, saved) in enumerate(zip(recomputed, stored)):
            found += mismatches(value, saved, f'{path}{position}.')
    elif abs(float(recomputed) - float(stored)) > TOLERANCE:
        found.append((path.rstrip('.'), f'{recomputed} contra {stored}'))
    return found


def recompute_all(models=DEFAULT_MODELS):
    """Una entrada por evaluación y por comparación versionada, con lo recalculado y lo que no coincide."""
    models = Path(models)
    results = []
    for report_path in sorted(models.glob('*/evaluacion_*/report.json')):
        report, recomputed = recompute_evaluation(report_path.parent)
        results.append({'kind': 'evaluación', 'folder': report_path.parent, 'report': report,
                        'recomputed': recomputed, 'mismatches': mismatches(recomputed, report)})
    for report_path in sorted(models.glob('comparacion_*/report.json')):
        report, recomputed = recompute_comparison(report_path.parent, models.parent)
        results.append({'kind': 'comparación', 'folder': report_path.parent, 'report': report,
                        'recomputed': recomputed, 'mismatches': mismatches(recomputed, report)})
    if not results:
        raise ValueError(f'No hay evaluaciones ni comparaciones en {models}')
    return results


def describe(result):
    report, recomputed = result['report'], result['recomputed']
    folder = result['folder']
    if result['kind'] == 'evaluación':
        metrics, (low, high) = recomputed['metrics'], recomputed['intervals_95']['f1']
        text = (f'{folder.parent.name} · {report["split"]} · {report["images"]} imágenes · '
                f'F1 {metrics["f1"]:.3f} ({low:.3f} a {high:.3f}) · AUC {metrics["auc"]:.3f} · '
                f'recall {metrics["recall"]:.1%} · especificidad {metrics["specificity"]:.1%}')
    else:
        difference, (low, high) = recomputed['differences']['f1_diferencia'], recomputed['intervals_95']['f1_diferencia']
        text = (f'{folder.name} · {report["split"]} · {report["difference"]} · '
                f'F1 {difference:+.3f} ({low:+.3f} a {high:+.3f})')
    return f'{text} · {"coincide" if not result["mismatches"] else "NO COINCIDE"}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelos', type=Path, default=DEFAULT_MODELS,
                        help=f'Carpeta con los modelos y las comparaciones (por defecto {DEFAULT_MODELS})')
    args = parser.parse_args()
    try:
        results = recompute_all(args.modelos)
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        raise SystemExit(1) from None
    for result in results:
        print(describe(result))
        for key, detail in result['mismatches']:
            print(f'    {key}: {detail}')
    failed = sum(bool(result['mismatches']) for result in results)
    print(f'\n{len(results) - failed} de {len(results)} resultados coinciden con sus report.json.')
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
