"""Split reproducible por paciente con búsqueda de proporciones aproximadas."""

import numpy as np

NAMES = ('train', 'val', 'test')


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
    """
    selection = config['selection']
    fraction = selection['positive_fraction']
    share = selection['no_finding_share']
    cap = selection['max_negatives_per_patient']
    repeat = selection.get('train_positive_repeat', 1)
    selected = {}
    for position, name in enumerate(NAMES):
        rows = sorted(splits[name], key=lambda r: r['image_path'])
        positives = [r for r in rows if r['target'] == 1]
        wanted = round(len(positives) * (repeat if name == 'train' else 1) * (1 - fraction) / fraction)
        no_finding = round(wanted * share)
        groups = [('No Finding', no_finding, [r for r in rows if r['target'] == 0 and r['target_original'] == 'No Finding']),
                  ('otros hallazgos', wanted - no_finding,
                   [r for r in rows if r['target'] == 0 and r['target_original'] != 'No Finding'])]
        rng = np.random.default_rng([config['seed'], position])
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
    return splits, 'seeded_patient_search'
