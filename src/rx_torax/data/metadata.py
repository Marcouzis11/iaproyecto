"""Adaptadores explícitos para etiquetas binarias y auditoría de archivos."""

import csv
import re
from collections import defaultdict
from pathlib import Path

from rx_torax.preprocessing.images import read_image


def read_metadata(config):
    source = Path(config["metadata"]).resolve()
    image_root = Path(config["image_root"]).resolve()
    dataset = config["dataset"]
    target = config["target"]
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or [])
        required = {"image_path", "patient_id", target}
        if dataset == "chexpert":
            required = {"Path", target}
        elif dataset == "nih":
            required = {"Image Index", "Patient ID", "Finding Labels"}
        if config.get("frontal_only") or config.get("views"):
            required.add({"chexpert": "Frontal/Lateral", "nih": "View Position",
                          "generic": "view"}[dataset])
        if not required <= fields:
            raise ValueError(f"Faltan columnas en {source.name}: {sorted(required - fields)}")
        raw = list(reader)
    if not raw:
        raise ValueError("El CSV no tiene registros")
    if dataset == "nih":
        vocabulary = {label.strip() for row in raw for label in row['Finding Labels'].split('|')}
        if target not in vocabulary or target == "No Finding":
            raise ValueError("El target NIH debe ser un hallazgo presente en Finding Labels")
        # NIH distribuye las imágenes en varios subdirectorios con el mismo nombre 'images'.
        index = defaultdict(list)
        for path in image_root.rglob('*'):
            if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}:
                index[path.name].append(path.resolve())
        official = {}
        lists = [source.parent / 'train_val_list.txt', source.parent / 'test_list.txt']
        if any(p.exists() for p in lists):
            if not all(p.is_file() for p in lists):
                raise ValueError('NIH: deben estar presentes train_val_list.txt y test_list.txt juntos')
            if any(row.get('split', '').strip() for row in raw):
                raise ValueError('NIH: elegir listas oficiales o columna split, no ambas')
            for split, path in zip(['train', 'test'], lists):
                for name in path.read_text(encoding='utf-8-sig').splitlines():
                    name = name.strip()
                    if not name:
                        continue
                    if name in official:
                        raise ValueError(f'NIH: imagen repetida en listas oficiales: {name}')
                    official[name] = split
            if set(official.values()) != {'train', 'test'}:
                raise ValueError('NIH: las dos listas oficiales deben contener imágenes')
    records, exclusions = [], []
    for number, row in enumerate(raw, start=2):
        item = {"source_row": number, "image_path": "", "patient_id": "",
                "target_original": "", "split": row.get("split", "").strip().lower()}
        if item['split'] == 'valid':
            item['split'] = 'val'
        reason = None
        if dataset == "nih":
            name = row['Image Index'].strip()
            matches = index.get(name, [])
            item.update(image_path=name, patient_id=row['Patient ID'].strip(),
                        target_original=row['Finding Labels'])
            if 'Follow-up #' in row:
                item['follow_up'] = int(row['Follow-up #'])
            if official:
                item['split'] = official.get(name, '')
                if not item['split']:
                    reason = 'missing_official_split'
            labels = {label.strip() for label in row['Finding Labels'].split('|')}
            if not labels or '' in labels or ('No Finding' in labels and len(labels) > 1):
                reason = reason or 'invalid_label'
            elif len(matches) != 1:
                reason = reason or ('missing_file' if not matches else 'ambiguous_filename')
            else:
                item['image_path'] = str(matches[0])
            item['target'] = int(target in labels)
            view = row.get('View Position', '').strip().upper()
            frontal = view in {'AP', 'PA'}
            allowed_view = not config.get('views') or view in config['views']
        else:
            relative = row['Path' if dataset == 'chexpert' else 'image_path'].strip().replace('\\', '/')
            item['image_path'] = relative
            if not relative:
                reason = 'missing_path'
            resolved = (image_root / relative).resolve()
            if not resolved.is_relative_to(image_root):
                reason = 'path_outside_image_root'
            item['image_path'] = str(resolved)
            if dataset == 'chexpert':
                match = re.search(r'(?:^|/)(patient\d+)(?:/|$)', relative)
                item['patient_id'] = match.group(1) if match else ''
                frontal = row.get('Frontal/Lateral', '').strip().lower() == 'frontal'
                allowed_view = True
            else:
                item['patient_id'] = row['patient_id'].strip()
                frontal = row.get('view', '').strip().upper() in {'AP', 'PA', 'FRONTAL'}
                allowed_view = not config.get('views') or row.get('view', '').strip().upper() in config['views']
            label = row[target].strip()
            item['target_original'] = label
            if label in {'0', '0.0', '1', '1.0'}:
                item['target'] = int(float(label))
            else:
                reason = reason or ({'': 'missing_label', '-1': 'uncertain_label',
                                     '-1.0': 'uncertain_label'}.get(label, 'invalid_label'))
        if not item['patient_id']:
            reason = reason or 'missing_patient_id'
        if config.get('frontal_only') and not frontal:
            reason = reason or 'non_frontal_view'
        if not allowed_view:
            reason = reason or 'excluded_view'
        if reason:
            exclusions.append(dict(item, reason=reason))
        else:
            records.append(item)
    # Una fila con split suministrado indica una partición oficial/explícita.
    # No se mezcla silenciosamente con filas sin asignación.
    supplied = [r.get('split', '').strip().lower() for r in raw]
    if any(supplied) and (not all(supplied) or any(s not in {'train','val','valid','test'} for s in supplied)):
        raise ValueError("La columna split debe estar completa y contener train, val/valid o test")
    return records, exclusions, len(raw)


def audit(records, exclusions):
    by_hash = defaultdict(list)
    for record in records:
        path = Path(record['image_path'])
        try:
            if not path.is_file():
                raise FileNotFoundError(path)
            _, info = read_image(path)
            by_hash[info['pixel_hash']].append(dict(record, **info))
        except (OSError, ValueError, Warning) as error:
            exclusions.append(dict(record, reason='missing_file' if isinstance(error, FileNotFoundError)
                                   else 'unreadable_image', detail=str(error)))
    kept = []
    for copies in by_hash.values():
        if len({r['target'] for r in copies}) > 1:
            reason = 'duplicate_conflicting_label'
        elif len({r['patient_id'] for r in copies}) > 1:
            reason = 'duplicate_across_patients'
        elif len({r['split'] for r in copies}) > 1:
            reason = 'duplicate_across_splits'
        else:
            kept.append(copies[0])
            copies = copies[1:]
            reason = 'duplicate_image'
        exclusions.extend(dict(r, reason=reason) for r in copies)
    return sorted(kept, key=lambda r: (r['patient_id'], r['image_path']))
