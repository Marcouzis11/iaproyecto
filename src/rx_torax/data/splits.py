"""Split reproducible por paciente con búsqueda de proporciones aproximadas."""

import numpy as np

NAMES = ('train', 'val', 'test')
FOLLOW_UP_BINS = ('0', '1-9', '10+')
NEGATIVE_KINDS = ('No Finding', 'otros hallazgos')


def follow_up_bin(value):
    return '0' if value == 0 else '1-9' if value < 10 else '10+'


def negative_kind(row):
    return 'No Finding' if row['target_original'] == 'No Finding' else 'otros hallazgos'


def check_composition(composition, no_finding_share):
    """Valida la mezcla de estudios previos pedida para positivas y negativas."""
    if not isinstance(composition, dict) or composition.keys() != {'splits', 'positives', 'negatives'}:
        raise ValueError('composition debe contener splits, positives y negatives')
    splits = composition['splits']
    if not isinstance(splits, list) or not splits or set(splits) - set(NAMES):
        raise ValueError('composition.splits debe ser una lista con train, val o test')
    negatives = composition['negatives']
    tables = [composition['positives']] + ([negatives[k] for k in NEGATIVE_KINDS] if isinstance(negatives, dict)
                                           and negatives.keys() == set(NEGATIVE_KINDS) else [None])
    if not all(isinstance(t, dict) and t.keys() == set(FOLLOW_UP_BINS) and
               all(isinstance(v, (int, float)) and v >= 0 for v in t.values()) for t in tables):
        raise ValueError(f'composition: cada tabla necesita proporciones para {list(FOLLOW_UP_BINS)}; '
                         f'negatives se divide en {list(NEGATIVE_KINDS)}')
    if abs(sum(tables[0].values()) - 1) > 1e-3 or abs(sum(map(sum, (t.values() for t in tables[1:]))) - 1) > 1e-3:
        raise ValueError('composition: las proporciones de positivas y de negativas deben sumar 1')
    if abs(sum(negatives['No Finding'].values()) - no_finding_share) > 1e-3:
        raise ValueError('composition: las negativas sin hallazgos deben sumar no_finding_share')


def quotas(total, shares):
    """Reparte total según shares por restos mayores, así la suma da exactamente total."""
    scale = sum(shares.values())
    exact = {key: total * share / scale for key, share in shares.items()}
    counts = {key: int(value) for key, value in exact.items()}
    for key in sorted(exact, key=lambda k: exact[k] - counts[k], reverse=True)[:total - sum(counts.values())]:
        counts[key] += 1
    return counts


def sample_positives(positives, shares, rng):
    """La mayor muestra de positivas que respeta la mezcla de estudios previos pedida."""
    by_bin = {key: [r for r in positives if follow_up_bin(r['follow_up']) == key] for key in FOLLOW_UP_BINS}
    total = min(int(len(by_bin[key]) / share) for key, share in shares.items() if share > 0)
    counts = quotas(total, shares)
    while any(counts[key] > len(by_bin[key]) for key in FOLLOW_UP_BINS):
        total -= 1
        counts = quotas(total, shares)
    return [by_bin[key][int(i)] for key in FOLLOW_UP_BINS for i in rng.permutation(len(by_bin[key]))[:counts[key]]]


def validate(splits):
    patients, hashes = set(), set()
    for name in NAMES:
        rows = splits[name]
        if {r['target'] for r in rows} != {0, 1}:
            raise ValueError(f"{name} necesita ejemplos de ambas clases tras la auditoría")
        current = {r['patient_id'] for r in rows}
        fingerprints = {r['pixel_hash'] for r in rows}
        if patients & current or hashes & fingerprints:
            raise ValueError("Fuga entre particiones: pacientes o imágenes repetidas")
        patients.update(current)
        hashes.update(fingerprints)


def partition(records, config, names, ratios):
    patients = sorted({r['patient_id'] for r in records})
    if len(patients) < 2 * len(names):
        raise ValueError(f"Se necesitan al menos {2*len(names)} pacientes y ambas clases en cada partición")
    ratios = np.array(ratios, dtype=float)
    sizes = [max(1, round(len(patients) * ratio)) for ratio in ratios[1:]]
    sizes.insert(0, len(patients) - sum(sizes))
    if sizes[0] < 1:
        raise ValueError("Las proporciones no dejan pacientes en train")
    lookup = {p: i for i, p in enumerate(patients)}
    counts = np.zeros((len(patients), 2), dtype=int)
    for row in records:
        counts[lookup[row['patient_id']], row['target']] += 1
    if np.any(counts.sum(axis=0) < len(names)):
        raise ValueError("No hay suficientes imágenes de cada clase para las particiones")
    rng = np.random.default_rng(config['seed'])
    best, best_score = None, float('inf')
    # Selección únicamente por tamaño y etiquetas, nunca por rendimiento del modelo.
    for _ in range(config.get('split_attempts', 1000)):
        order = rng.permutation(len(patients))
        groups = np.split(order, np.cumsum(sizes)[:-1])
        totals = np.array([counts[group].sum(axis=0) for group in groups])
        if np.any(totals == 0):
            continue
        score = float(np.square(totals / counts.sum(axis=0) - ratios[:, None]).sum())
        if score < best_score:
            best_score, best = score, groups
    if best is None:
        raise ValueError("No se encontró split con ambas clases. Revisar pacientes/clases o aumentar split_attempts")
    assignment = {patients[int(i)]: name for name, group in zip(names, best) for i in group}
    splits = {name: [dict(r, split=name) for r in records if assignment[r['patient_id']] == name]
              for name in names}
    return splits


def select_balanced(splits, config):
    """Conserva todos los positivos y submuestrea negativos, igual en cada conjunto.

    Se aplica después del split por paciente. Cada conjunto usa su propio generador,
    derivado de la semilla, y la elección depende solo de etiquetas y pacientes.
    train_positive_repeat suma negativos solo en train, para el entrenamiento que
    repite positivos; val y test quedan iguales. Las repeticiones no se exportan.
    composition fija la mezcla de estudios previos en los conjuntos que nombra. En val
    y test también submuestrea positivas; en train las conserva todas.
    """
    selection = config['selection']
    fraction = selection['positive_fraction']
    share = selection['no_finding_share']
    cap = selection['max_negatives_per_patient']
    repeat = selection.get('train_positive_repeat', 1)
    composition = selection.get('composition')
    if composition and any('follow_up' not in r for rows in splits.values() for r in rows):
        raise ValueError('composition necesita la columna Follow-up # de NIH')
    selected = {}
    for position, name in enumerate(NAMES):
        rows = sorted(splits[name], key=lambda r: r['image_path'])
        rng = np.random.default_rng([config['seed'], position])
        mixed = bool(composition) and name in composition['splits']
        positives = [r for r in rows if r['target'] == 1]
        if mixed and name != 'train':
            positives = sample_positives(positives, composition['positives'], rng)
        wanted = round(len(positives) * (repeat if name == 'train' else 1) * (1 - fraction) / fraction)
        if mixed:
            counts = quotas(wanted, {(k, b): composition['negatives'][k][b] for k in NEGATIVE_KINDS
                                     for b in FOLLOW_UP_BINS})
            # Primero los grupos con más estudios previos, que son los más escasos.
            groups = [(f'{k}, {b} estudios previos', counts[k, b],
                       [r for r in rows if r['target'] == 0 and negative_kind(r) == k
                        and follow_up_bin(r['follow_up']) == b])
                      for b in reversed(FOLLOW_UP_BINS) for k in NEGATIVE_KINDS]
        else:
            no_finding = round(wanted * share)
            groups = [(k, count, [r for r in rows if r['target'] == 0 and negative_kind(r) == k])
                      for k, count in zip(NEGATIVE_KINDS, (no_finding, wanted - no_finding))]
        negatives, per_patient = [], {}
        for label, count, candidates in groups:
            chosen = []
            for index in rng.permutation(len(candidates)):
                if len(chosen) == count:
                    break
                row = candidates[int(index)]
                if per_patient.get(row['patient_id'], 0) < cap:
                    per_patient[row['patient_id']] = per_patient.get(row['patient_id'], 0) + 1
                    chosen.append(row)
            if len(chosen) < count:
                raise ValueError(f"{name}: no alcanzan los negativos de '{label}' ({len(chosen)} de {count})")
            negatives.extend(chosen)
        selected[name] = sorted(positives + negatives, key=lambda r: (r['patient_id'], r['image_path']))
    return selected


def make_splits(records, config):
    suffix = ''
    if config.get('exclude_official_test'):
        if not any(r['split'] == 'test' for r in records):
            raise ValueError('exclude_official_test necesita las listas oficiales de NIH')
        # El test oficial ya se usó: sus imágenes quedan afuera y los tres conjuntos salen de train_val.
        records = [dict(r, split='') for r in records if r['split'] != 'test']
        suffix = '_without_official_test'
    supplied = {r['split'] for r in records if r['split']}
    if supplied:
        splits = {name: [r for r in records if r['split'] == name] for name in NAMES}
        method = 'explicit_three_way_split'
        if supplied == {'train', 'test'}:
            if {r['patient_id'] for r in splits['train']} & {r['patient_id'] for r in splits['test']}:
                raise ValueError('Fuga entre train y test oficiales: pacientes repetidos')
            a, b, _ = config['ratios']
            internal = partition(splits['train'], config, ('train', 'val'), [a/(a+b), b/(a+b)])
            splits.update(internal)
            method = 'explicit_test_patient_validation_from_train'
        if config.get('selection'):
            splits = select_balanced(splits, config)
        validate(splits)
        return splits, method
    splits = partition(records, config, NAMES, config['ratios'])
    if config.get('selection'):
        splits = select_balanced(splits, config)
    validate(splits)
    return splits, 'seeded_patient_search' + suffix
