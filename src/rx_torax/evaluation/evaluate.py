"""CLI: rx-evaluar --modelo models/modelo_b_densenet121_v1 --conjunto test.

Usa el umbral guardado en modelo.pt, que se eligió con validación; acá nunca se recalcula.
Cada evaluación queda en <modelo>/evaluacion_<conjunto> y no se pisa: test se mira una sola vez.
"""

import argparse
import csv
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from rx_torax.evaluation.metrics import at_prevalence, binary_metrics, roc_auc, roc_curve, trivial_baselines
from rx_torax.training.model import build_model
from rx_torax.training.train import load_split, pick_device, predict_logits, versions, write_csv


# Prevalencia de Effusion en todas las PA de NIH y en las PA del test oficial (docs/SPLITS_NIH_EFFUSION.md).
PREVALENCES = (0.098, 0.158)
BOOTSTRAP = {'unit': 'patient', 'rounds': 2000, 'seed': 42}
# Colores de las figuras: serie 1 y 2 de la paleta categórica, tinta y superficie.
COLORS = {'first': '#2a78d6', 'second': '#eb6834', 'ink': '#0b0b0b', 'muted': '#52514e', 'grid': '#e4e3df',
          'surface': '#fcfcfb'}


def load_model(model_dir, device):
    artifact = torch.load(Path(model_dir) / 'modelo.pt', map_location='cpu', weights_only=True)
    model = build_model(artifact['architecture'], False)
    model.load_state_dict(artifact['state_dict'])
    return artifact, model.to(device).eval()


def score(artifact, model, images, indices, device, batch_size=64):
    logits = predict_logits(model, images, indices, artifact['train_mean'], artifact['train_std'], batch_size, device)
    return torch.sigmoid(logits).numpy().astype(np.float64)


def read_rows(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def load_rows(data, split, labels):
    rows = read_rows(data / f'{split}.csv')
    if [int(r['target']) for r in rows] != labels.tolist():
        raise ValueError(f'{split}.csv no coincide con y_{split}.npy')
    return rows


def read_nih_metadata(data):
    """Edad, sexo y seguimiento de NIH, solo para describir subgrupos; no son entradas del modelo."""
    path = data / 'config.json'
    config = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    metadata = Path(config.get('metadata', ''))
    if config.get('dataset') != 'nih' or not metadata.is_file():
        return None
    return {row['Image Index']: row for row in read_rows(metadata)}


def bootstrap(labels, patients, statistic, rounds, seed):
    """Remuestrea pacientes, no imágenes: las de un mismo paciente no son independientes."""
    _, inverse = np.unique(patients, return_inverse=True)
    order = np.argsort(inverse, kind='stable')
    groups = np.split(order, np.cumsum(np.bincount(inverse))[:-1])
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(rounds):
        chosen = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        if 0 < labels[chosen].sum() < len(chosen):
            samples.append(statistic(chosen))
    return samples


def intervals(samples):
    """Percentiles 2,5 y 97,5 de cada estadístico remuestreado."""
    return {key: [float(np.percentile([s[key] for s in samples], q)) for q in (2.5, 97.5)] for key in samples[0]}


def summary(labels, scores, threshold):
    metrics = binary_metrics(labels, scores, threshold)
    return {'auc': roc_auc(labels, scores), **{k: metrics[k] for k in ('f1', 'recall', 'specificity', 'precision')}}


def group_metrics(labels, scores, threshold, mask):
    y, predicted = labels[mask], scores[mask] >= threshold
    positives, negatives = int(y.sum()), int(len(y) - y.sum())
    return {'images': int(len(y)), 'positives': positives,
            'auc': roc_auc(y, scores[mask]) if positives and negatives else None,
            'recall': float(predicted[y == 1].mean()) if positives else None,
            'specificity': float((~predicted[y == 0]).mean()) if negatives else None}


def subgroups(labels, scores, threshold, rows, target, metadata=None):
    """Los grupos por hallazgo comparan una parte de una clase contra toda la otra clase."""
    findings = np.array([r['target_original'] for r in rows])
    positive, no_finding, alone = labels == 1, findings == 'No Finding', findings == target
    masks = {'negativos_sin_hallazgos': positive | (~positive & no_finding),
             'negativos_con_otros_hallazgos': positive | (~positive & ~no_finding),
             'positivos_sin_otros_hallazgos': ~positive | (positive & alone),
             'positivos_con_otros_hallazgos': ~positive | (positive & ~alone)}
    if metadata:
        info = [metadata[Path(r['image_path']).name] for r in rows]
        age = np.array([int(i['Patient Age']) for i in info])
        sex = np.array([i['Patient Sex'] for i in info])
        follow_up = np.array([int(i['Follow-up #']) for i in info])
        masks |= {'sexo_F': sex == 'F', 'sexo_M': sex == 'M', 'edad_menor_40': age < 40,
                  'edad_40_59': (age >= 40) & (age < 60), 'edad_60_o_mas': age >= 60,
                  'seguimiento_0': follow_up == 0, 'seguimiento_1_9': (follow_up >= 1) & (follow_up < 10),
                  'seguimiento_10_o_mas': follow_up >= 10}
    return {name: group_metrics(labels, scores, threshold, mask) for name, mask in masks.items()}


def cpu_milliseconds(model_dir, images, indices, count=20):
    """Mediana por imagen en CPU y de a una, como en una demo."""
    device = torch.device('cpu')
    artifact, model = load_model(model_dir, device)
    times = []
    for index in indices[:count + 1]:
        started = time.perf_counter()
        score(artifact, model, images, np.array([index]), device)
        times.append(time.perf_counter() - started)
    return float(np.median(times[1:]) * 1000)


def pyplot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.facecolor': COLORS['surface'], 'axes.facecolor': COLORS['surface'],
                         'axes.edgecolor': COLORS['grid'], 'axes.labelcolor': COLORS['muted'],
                         'xtick.color': COLORS['muted'], 'ytick.color': COLORS['muted'], 'text.color': COLORS['ink'],
                         'axes.grid': True, 'grid.color': COLORS['grid'], 'grid.linewidth': 0.8,
                         'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})
    return plt


def save_figures(path, labels, scores, threshold, title):
    plt = pyplot()
    metrics = binary_metrics(labels, scores, threshold)
    fpr, tpr = roc_curve(labels, scores)
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    axes[0].plot([0, 1], [0, 1], color=COLORS['muted'], ls='--', lw=1, label='Azar')
    axes[0].plot(fpr, tpr, color=COLORS['first'], lw=2, label=f'Modelo (AUC {roc_auc(labels, scores):.3f})')
    axes[0].scatter([1 - metrics['specificity']], [metrics['recall']], s=60, color=COLORS['ink'], zorder=3,
                    edgecolors=COLORS['surface'], linewidths=2, label=f'Umbral de val ({threshold:.3f})')
    axes[0].set(xlabel='1 − especificidad', ylabel='Recall', title='Curva ROC', xlim=(0, 1), ylim=(0, 1.01))
    axes[0].legend(loc='lower right')
    matrix = np.array([[metrics['tn'], metrics['fp']], [metrics['fn'], metrics['tp']]])
    axes[1].imshow(matrix, cmap='Blues', vmin=0, vmax=matrix.max() * 1.15)
    axes[1].grid(False)
    for (row, column), value in np.ndenumerate(matrix):
        axes[1].text(column, row, f'{value}\n{value / matrix[row].sum():.1%} de la fila', ha='center', va='center',
                     color='white' if value > matrix.max() / 2 else COLORS['ink'], fontsize=11)
    axes[1].set(xticks=[0, 1], yticks=[0, 1], xticklabels=['Negativo', 'Positivo'],
                yticklabels=['Negativo', 'Positivo'], xlabel='Predicción', ylabel='Real', title='Matriz de confusión')
    bins = np.linspace(0, 1, 41)
    axes[2].hist(scores[labels == 0], bins=bins, color=COLORS['second'], alpha=0.75, label='Negativos',
                 edgecolor=COLORS['surface'], linewidth=1)
    axes[2].hist(scores[labels == 1], bins=bins, color=COLORS['first'], alpha=0.75, label='Positivos',
                 edgecolor=COLORS['surface'], linewidth=1)
    axes[2].axvline(threshold, color=COLORS['ink'], lw=1.5, ls='--', label='Umbral')
    axes[2].set(xlabel='Probabilidad estimada', ylabel='Imágenes', title='Puntajes por clase real')
    axes[2].legend()
    figure.suptitle(title)
    figure.tight_layout()
    figure.savefig(path, dpi=130)
    plt.close(figure)


def save_examples(path, images, labels, scores, threshold, findings, per_kind=5):
    """Los casos más seguros de cada celda de la matriz: aciertos y errores con mayor convicción."""
    plt = pyplot()
    predicted = scores >= threshold
    kinds = [('Falsos negativos (menor puntaje)', (labels == 1) & ~predicted, 1),
             ('Falsos positivos (mayor puntaje)', (labels == 0) & predicted, -1),
             ('Verdaderos positivos (mayor puntaje)', (labels == 1) & predicted, -1),
             ('Verdaderos negativos (menor puntaje)', (labels == 0) & ~predicted, 1)]
    figure, axes = plt.subplots(len(kinds), per_kind, figsize=(2.6 * per_kind, 3.1 * len(kinds)))
    for row, (title, mask, sign) in enumerate(kinds):
        chosen = np.flatnonzero(mask)[np.argsort(sign * scores[mask], kind='stable')][:per_kind]
        for column in range(per_kind):
            axis = axes[row, column]
            axis.axis('off')
            if column < len(chosen):
                index = chosen[column]
                axis.imshow(images[index], cmap='gray', vmin=0, vmax=1)
                axis.set_title(f'{scores[index]:.2f} · {findings[index][:28]}', fontsize=8)
        axes[row, 0].text(-0.08, 0.5, title, transform=axes[row, 0].transAxes, rotation=90, ha='right',
                          va='center', fontsize=9)
    figure.tight_layout()
    figure.savefig(path, dpi=110)
    plt.close(figure)


def evaluate(model_dir, split='val', data=None, device='auto'):
    model_dir = Path(model_dir)
    output = model_dir / f'evaluacion_{split}'
    if output.exists():
        raise ValueError(f'{output} ya existe: {split} ya se evaluó con este modelo y no se repite')
    training = json.loads((model_dir / 'report.json').read_text(encoding='utf-8'))
    data = Path(data or training['config']['data'])
    device = pick_device(device)
    artifact, model = load_model(model_dir, device)
    images, labels, indices = load_split(data, split)
    rows = load_rows(data, split, labels)
    started = time.perf_counter()
    scores = score(artifact, model, images, indices, device)
    seconds = time.perf_counter() - started
    threshold = artifact['threshold']
    patients = np.array([r['patient_id'] for r in rows])
    samples = bootstrap(labels, patients, lambda chosen: summary(labels[chosen], scores[chosen], threshold),
                        BOOTSTRAP['rounds'], BOOTSTRAP['seed'])
    metrics = {'auc': roc_auc(labels, scores), **binary_metrics(labels, scores, threshold)}
    stage = output.with_name(output.name + '.parcial')
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    predicted = scores >= threshold
    write_csv(stage / f'predicciones_{split}.csv',
              [{'array_index': int(index), 'image': Path(row['image_path']).name, 'patient_id': row['patient_id'],
                'target': int(label), 'target_original': row['target_original'], 'score': float(value),
                'predicted': int(guess)}
               for index, row, label, value, guess in zip(indices, rows, labels, scores, predicted)])
    title = f'{model_dir.name} · {split} · {len(labels)} imágenes'
    save_figures(stage / 'resultados.png', labels, scores, threshold, title)
    save_examples(stage / 'ejemplos.png', images, labels, scores, threshold, [r['target_original'] for r in rows])
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'model': str(model_dir), 'data': str(data),
              'split': split, 'device': str(device), 'versions': versions(), 'target': artifact['target'],
              'images': len(labels), 'patients': int(len(set(patients))), 'positives': int(labels.sum()),
              'threshold': threshold, 'threshold_source': 'validación, guardado en modelo.pt',
              'metrics': metrics, 'intervals_95': intervals(samples),
              'bootstrap': BOOTSTRAP | {'valid_rounds': len(samples)},
              'metrics_threshold_0_5': binary_metrics(labels, scores, 0.5),
              'baselines': trivial_baselines(labels),
              'at_prevalence': [at_prevalence(metrics['recall'], metrics['specificity'], p) for p in PREVALENCES],
              'subgroups': subgroups(labels, scores, threshold, rows, artifact['target'], read_nih_metadata(data)),
              'subgroups_note': 'Los grupos por hallazgo comparan esa parte de una clase contra toda la otra.',
              'milliseconds_per_image_batch': seconds / len(labels) * 1000,
              'milliseconds_per_image_cpu': cpu_milliseconds(model_dir, images, indices)}
    (stage / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    stage.rename(output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo', type=Path, required=True)
    parser.add_argument('--conjunto', choices=['val', 'test'], default='val')
    parser.add_argument('--datos', type=Path, help='Carpeta preparada; por defecto, la usada para entrenar')
    parser.add_argument('--dispositivo', default='auto')
    args = parser.parse_args()
    report = evaluate(args.modelo, args.conjunto, args.datos, args.dispositivo)
    print(json.dumps({'metrics': report['metrics'], 'intervals_95': report['intervals_95']}, indent=2))


if __name__ == '__main__':
    main()
