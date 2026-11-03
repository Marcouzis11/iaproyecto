"""CLI: rx-comparar --modelos models/modelo_a_densenet121_v1 models/modelo_b_densenet121_v1 --salida models/comparacion_val.

Compara dos modelos sobre el mismo conjunto de validación, con bootstrap pareado por paciente.
Sirve para elegir el modelo final, así que no admite test.
"""

import argparse
import csv
import filecmp
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from rx_torax.evaluation.evaluate import (BOOTSTRAP, COLORS, bootstrap, intervals, load_model, load_rows, pyplot,
                                          score, summary)
from rx_torax.evaluation.metrics import binary_metrics, roc_auc, roc_curve
from rx_torax.training.train import load_split, pick_device, versions


VAL_FILES = ('X_val.npy', 'y_val.npy', 'val.csv')


def same_validation(first, second):
    return first.resolve() == second.resolve() or all(
        filecmp.cmp(first / name, second / name, shallow=False) for name in VAL_FILES)


def read_history(model_dir):
    with (model_dir / 'historial.csv').open(newline='', encoding='utf-8') as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def save_figure(path, labels, scored, histories):
    plt = pyplot()
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    axes[0].plot([0, 1], [0, 1], color=COLORS['muted'], ls='--', lw=1, label='Azar')
    for (name, (scores, _)), color in zip(scored.items(), (COLORS['first'], COLORS['second'])):
        fpr, tpr = roc_curve(labels, scores)
        axes[0].plot(fpr, tpr, color=color, lw=2, label=f'{name} (AUC {roc_auc(labels, scores):.3f})')
    axes[0].set(xlabel='1 − especificidad', ylabel='Recall', title='Curva ROC en validación', xlim=(0, 1),
                ylim=(0, 1.01))
    axes[0].legend(loc='lower right')
    for (name, history), color in zip(histories.items(), (COLORS['first'], COLORS['second'])):
        epochs = [row['epoch'] for row in history]
        axes[1].plot(epochs, [row['val_auc'] for row in history], color=color, lw=2, marker='o', ms=6, label=name)
        axes[2].plot(epochs, [row['train_loss'] for row in history], color=color, lw=2, ls='--', marker='o', ms=6,
                     label=f'{name} train')
        axes[2].plot(epochs, [row['val_loss'] for row in history], color=color, lw=2, marker='o', ms=6,
                     label=f'{name} val')
    axes[1].set(xlabel='Época', ylabel='AUC', title='AUC de validación por época')
    axes[1].legend()
    axes[2].set(xlabel='Época', ylabel='Pérdida (BCE)', title='Pérdida por época')
    axes[2].legend()
    figure.tight_layout()
    figure.savefig(path, dpi=130)
    plt.close(figure)


def compare(model_dirs, output, names=None, device='auto'):
    output = Path(output)
    if output.exists():
        raise ValueError(f'La salida ya existe: {output}')
    model_dirs = [Path(path) for path in model_dirs]
    if len(model_dirs) != 2:
        raise ValueError('Se comparan exactamente dos modelos')
    names = names or [path.name for path in model_dirs]
    reports = [json.loads((path / 'report.json').read_text(encoding='utf-8')) for path in model_dirs]
    datas = [Path(report['config']['data']) for report in reports]
    if not same_validation(*datas):
        raise ValueError('Los modelos no se validaron con el mismo conjunto: la comparación no sería pareada')
    device = pick_device(device)
    images, labels, indices = load_split(datas[0], 'val')
    rows = load_rows(datas[0], 'val', labels)
    scored = {}
    for name, path in zip(names, model_dirs):
        artifact, model = load_model(path, device)
        scored[name] = (score(artifact, model, images, indices, device), artifact['threshold'])
    (first, (s1, t1)), (second, (s2, t2)) = scored.items()

    def paired(chosen):
        a, b = summary(labels[chosen], s1[chosen], t1), summary(labels[chosen], s2[chosen], t2)
        return {f'{key}_diferencia': b[key] - a[key] for key in a}

    patients = np.array([r['patient_id'] for r in rows])
    samples = bootstrap(labels, patients, paired, BOOTSTRAP['rounds'], BOOTSTRAP['seed'])
    point = {first: summary(labels, s1, t1), second: summary(labels, s2, t2)}
    right1, right2 = (s1 >= t1) == (labels == 1), (s2 >= t2) == (labels == 1)
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'split': 'val', 'device': str(device),
              'versions': versions(), 'models': dict(zip(names, map(str, model_dirs))), 'data': str(datas[0]),
              'images': len(labels), 'patients': int(len(set(patients))), 'positives': int(labels.sum()),
              'metrics': {name: point[name] | binary_metrics(labels, *scored[name]) for name in names},
              'difference': f'{second} − {first}',
              'differences': paired(np.arange(len(labels))),
              'intervals_95': intervals(samples),
              'probability_second_better': {key: float(np.mean([s[key] > 0 for s in samples])) for key in samples[0]},
              'bootstrap': BOOTSTRAP | {'valid_rounds': len(samples)},
              'disagreements': int(((s1 >= t1) != (s2 >= t2)).sum()),
              'only_first_right': int((right1 & ~right2).sum()), 'only_second_right': int((~right1 & right2).sum()),
              # Los reportes anteriores a repeat_positives usaban una muestra por imagen.
              'training': {name: {key: report[key] for key in ('best_epoch', 'epochs_run', 'train_seconds',
                                                               'train_images')}
                           | {'train_samples_per_epoch': report.get('train_samples_per_epoch', report['train_images'])}
                           for name, report in zip(names, reports)},
              'correlation': float(np.corrcoef(s1, s2)[0, 1]),
              'note': 'Época y umbral se eligieron con val: los valores absolutos son optimistas; la diferencia es '
                      'pareada sobre las mismas imágenes y pacientes.'}
    stage = output.with_name(output.name + '.parcial')
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    save_figure(stage / 'comparacion_val.png', labels, scored,
                {name: read_history(path) for name, path in zip(names, model_dirs)})
    (stage / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    stage.rename(output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelos', type=Path, nargs=2, required=True)
    parser.add_argument('--nombres', nargs=2, help='Nombres cortos para tablas y figuras')
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--dispositivo', default='auto')
    args = parser.parse_args()
    report = compare(args.modelos, args.salida, args.nombres, args.dispositivo)
    print(json.dumps({'differences': report['differences'], 'intervals_95': report['intervals_95']}, indent=2,
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
