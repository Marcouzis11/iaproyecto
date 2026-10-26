"""CLI: rx-preparar --config configs/chexpert.json."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from rx_torax import __version__
from rx_torax.data.metadata import audit, read_metadata
from rx_torax.data.splits import NAMES, make_splits
from rx_torax.preprocessing.images import transform


DEFAULTS = {'image_size': 224, 'seed': 42, 'ratios': [0.7, 0.15, 0.15],
            'normalization': 'unit', 'frontal_only': False, 'views': None, 'split_attempts': 1000}


def load_config(path):
    with Path(path).open(encoding='utf-8-sig') as stream:
        given = json.load(stream)
    required = {'dataset', 'target', 'metadata', 'image_root', 'output'}
    allowed = required | set(DEFAULTS)
    if not required <= given.keys() or given.keys() - allowed:
        raise ValueError(f"Configuración: faltan {sorted(required-given.keys())}; "
                         f"claves desconocidas {sorted(given.keys()-allowed)}")
    config = DEFAULTS | given
    if config['dataset'] not in {'generic', 'nih', 'chexpert'}:
        raise ValueError('dataset debe ser generic, nih o chexpert')
    if not isinstance(config['target'], str) or not config['target'].strip():
        raise ValueError('target debe ser un nombre no vacío')
    for name in ['image_size', 'split_attempts', 'seed']:
        if type(config[name]) is not int or config[name] < (0 if name == 'seed' else 1):
            raise ValueError(f'{name} debe ser un entero válido')
    if not 8 <= config['image_size'] <= 2048:
        raise ValueError('image_size debe estar entre 8 y 2048')
    ratios = np.asarray(config['ratios'], dtype=float)
    if ratios.shape != (3,) or not np.isfinite(ratios).all() or np.any(ratios <= 0) or not np.isclose(ratios.sum(), 1):
        raise ValueError('ratios debe contener tres proporciones positivas que sumen 1')
    if type(config['frontal_only']) is not bool:
        raise ValueError('frontal_only debe ser true o false')
    views = config['views']
    if views is not None:
        if config['dataset'] == 'chexpert':
            raise ValueError('views solo se admite para nih y generic')
        if not isinstance(views, list) or not views or not all(isinstance(v, str) and v.strip() for v in views):
            raise ValueError('views debe ser una lista no vacía de vistas, por ejemplo ["PA"]')
        config['views'] = sorted({v.strip().upper() for v in views})
    if config['normalization'] not in {'unit', 'zscore'}:
        raise ValueError('normalization debe ser unit o zscore')
    for key in ['metadata', 'image_root', 'output']:
        config[key] = str(Path(config[key]).resolve())
    if not Path(config['metadata']).is_file() or not Path(config['image_root']).is_dir():
        raise ValueError('Faltan el CSV o la carpeta de imágenes; revisar metadata e image_root')
    output = Path(config['output'])
    inputs = [Path(config['image_root']), Path(config['metadata']).parent]
    if any(output == p or output.is_relative_to(p) or p.is_relative_to(output) for p in inputs):
        raise ValueError('output debe estar separado de las carpetas de entrada')
    if output.exists():
        raise ValueError(f'La salida ya existe: {output}. Usar otra ruta para conservar el experimento')
    return config


def write_csv(path, records, fields=None):
    fields = fields or sorted({key for row in records for key in row}) or ['source_row', 'reason']
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def prepare(config_path):
    config = load_config(config_path)
    records, exclusions, source_count = read_metadata(config)
    print(f'Metadatos: {source_count} filas. Auditando {len(records)} imágenes...', flush=True)
    records = audit(records, exclusions)
    output = Path(config['output'])
    try:
        splits, method = make_splits(records, config)
    except ValueError:
        # Un diagnóstico separado permite revisar exclusiones aun si no hay un split viable.
        diagnostic = output.with_name(output.name + '.audit.csv')
        diagnostic.parent.mkdir(parents=True, exist_ok=True)
        if not diagnostic.exists():
            write_csv(diagnostic, exclusions)
        print(f'No se exportaron conjuntos. Diagnóstico de auditoría: {diagnostic}', file=sys.stderr)
        raise
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=output.name + '.preparing-', dir=output.parent)).resolve()
    try:
        size = config['image_size']
        estimated_bytes = sum(len(rows) for rows in splits.values()) * size * size * 4
        if shutil.disk_usage(stage).free < estimated_bytes * 1.1:
            raise ValueError(f'Espacio insuficiente; arrays necesitan aproximadamente {estimated_bytes/2**30:.2f} GiB')
        total, squared, count = 0.0, 0.0, 0
        print('Calculando estadísticas solo sobre train...', flush=True)
        for row in splits['train']:
            image = transform(Path(row['image_path']), size, row['pixel_hash']).astype(np.float64)
            total += float(image.sum())
            squared += float(np.square(image).sum())
            count += image.size
        mean = total / count
        std = float(np.sqrt(max(0.0, squared / count - mean * mean)))
        if config['normalization'] == 'zscore' and std < 1e-8:
            raise ValueError('Train tiene varianza nula; no se puede estandarizar')
        stats = {'normalization': config['normalization'], 'train_mean': mean, 'train_std': std,
                 'statistics_source': 'train_only_after_resize_and_padding', 'image_size': size,
                 'grayscale': True, 'resize': 'bilinear_preserve_aspect_black_padding',
                 'unit_scale': 'uint8/255 or uint16/65535', 'shape': 'N,H,W', 'dtype': 'float32'}
        report = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
                  'project_version': __version__, 'python': sys.version,
                  'dependencies': {p: importlib.metadata.version(p) for p in ['numpy', 'Pillow']},
                  'metadata_sha256': hashlib.sha256(Path(config['metadata']).read_bytes()).hexdigest(),
                  'source_rows': source_count, 'accepted_images': len(records),
                  'excluded_rows': len(exclusions), 'exclusion_reasons': dict(Counter(r['reason'] for r in exclusions)),
                  'split_method': method, 'seed': config['seed'], 'splits': {},
                  'checks': {'patients_disjoint': True, 'exact_pixels_disjoint': True,
                             'both_classes_each_split': True},
                  'limitations': ['Exact duplicate detection only; near duplicates require further review.',
                                 'No automatic clinical quality or label correctness verification.',
                                 'No resampling, augmentation, outlier deletion or label imputation.']}
        for name in NAMES:
            rows = splits[name]
            array = np.lib.format.open_memmap(stage / f'X_{name}.npy', mode='w+', dtype=np.float32,
                                               shape=(len(rows), size, size))
            try:
                for i, row in enumerate(rows):
                    image = transform(Path(row['image_path']), size, row['pixel_hash'])
                    if config['normalization'] == 'zscore':
                        image = (image - mean) / std
                    array[i] = image
                array.flush()
            finally:
                # Cerrar el mapping también en Windows antes de renombrar/eliminar.
                array._mmap.close()
                del array
            np.save(stage / f'y_{name}.npy', np.array([r['target'] for r in rows], dtype=np.int64), allow_pickle=False)
            exported = [dict(r, array_index=i) for i, r in enumerate(rows)]
            write_csv(stage / f'{name}.csv', exported)
            report['splits'][name] = {'images': len(rows), 'patients': len({r['patient_id'] for r in rows}),
                                     'class_0': sum(r['target'] == 0 for r in rows),
                                     'class_1': sum(r['target'] == 1 for r in rows),
                                     'image_fraction': len(rows) / len(records)}
            print(f'{name}: {len(rows)} imágenes exportadas', flush=True)
        assert len(records) + len(exclusions) == source_count
        write_csv(stage / 'exclusiones.csv', exclusions)
        write_json(stage / 'config.json', config)
        write_json(stage / 'preprocessing.json', stats)
        write_json(stage / 'report.json', report)
        write_json(stage / 'labels.json', {'target': config['target'], '0': 'negative_annotation',
                                         '1': 'positive_annotation',
                                         'note': 'Negativo para el hallazgo no significa radiografía normal.'})
        stage.rename(output)
    finally:
        if stage.exists():
            if stage.parent != output.parent.resolve() or not stage.name.startswith(output.name + '.preparing-'):
                raise RuntimeError('Ruta temporal inesperada; no se elimina')
            shutil.rmtree(stage)
    print(f'Preparación terminada: {output}', flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description='Preparar radiografías para clasificación binaria, sin entrenar.')
    parser.add_argument('--config', required=True, help='JSON; rutas relativas al directorio de ejecución')
    args = parser.parse_args()
    try:
        prepare(args.config)
    except (ValueError, OSError, KeyError, TypeError, csv.Error) as error:
        parser.exit(2, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
