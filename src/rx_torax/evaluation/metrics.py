"""AUC, métricas con umbral y referencias triviales."""

import numpy as np


def roc_auc(labels, scores):
    """Probabilidad de que un positivo puntúe más que un negativo; los empates valen 0,5."""
    labels = np.asarray(labels).astype(int)
    positives = int(labels.sum())
    negatives = len(labels) - positives
    if not positives or not negatives:
        raise ValueError('El AUC necesita positivos y negativos')
    _, inverse, counts = np.unique(np.asarray(scores), return_inverse=True, return_counts=True)
    ends = np.cumsum(counts)
    ranks = (ends - (counts - 1) / 2)[inverse]
    return float((ranks[labels == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def binary_metrics(labels, scores, threshold):
    labels = np.asarray(labels).astype(int)
    predicted = np.asarray(scores) >= threshold
    tp = int((predicted & (labels == 1)).sum())
    fp = int((predicted & (labels == 0)).sum())
    fn = int((~predicted & (labels == 1)).sum())
    tn = int((~predicted & (labels == 0)).sum())
    ratio = lambda top, bottom: top / bottom if bottom else 0.0
    return {'threshold': float(threshold), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'accuracy': ratio(tp + tn, len(labels)), 'precision': ratio(tp, tp + fp),
            'recall': ratio(tp, tp + fn), 'specificity': ratio(tn, tn + fp),
            'f1': ratio(2 * tp, 2 * tp + fp + fn)}


def best_threshold(labels, scores):
    """Puntaje que maximiza F1. Elegirlo solo con validación, nunca con test."""
    labels = np.asarray(labels).astype(int)
    scores = np.asarray(scores)
    order = np.argsort(-scores, kind='stable')
    ordered = scores[order]
    tp = np.cumsum(labels[order])
    fp = np.cumsum(1 - labels[order])
    f1 = 2 * tp / (2 * tp + fp + labels.sum() - tp)
    # Un puntaje repetido no puede separarse: solo vale el último de cada grupo de empates.
    valid = np.append(ordered[1:] != ordered[:-1], True)
    return float(ordered[np.argmax(np.where(valid, f1, -1.0))])


def trivial_baselines(labels):
    """Referencias sin modelo: predecir siempre positivo o siempre negativo."""
    count = len(labels)
    return {'always_positive': binary_metrics(labels, np.ones(count), 1.0),
            'always_negative': binary_metrics(labels, np.zeros(count), 1.0)}
