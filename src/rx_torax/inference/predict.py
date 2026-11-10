"""CLI: rx-predecir imagen.png [otra.png ...] [--json] [--modelo models/modelo_b_densenet121_v1].

Aplica la misma transformación que la preparación y el umbral guardado en modelo.pt, elegido en validación.
El modelo se entrenó con radiografías PA de NIH: con otras vistas u otras imágenes el puntaje no significa nada.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from rx_torax.evaluation.evaluate import load_model, score
from rx_torax.preprocessing.images import transform
from rx_torax.training.train import pick_device, write_csv

DEFAULT_MODEL = Path('models/modelo_b_densenet121_v1')


def load_image(path, size):
    try:
        return transform(path, size)
    except (OSError, ValueError) as error:
        raise ValueError(f'{path}: {error}') from error


def predict(model_dir, paths, device='auto'):
    paths = [Path(path) for path in paths]
    if not paths:
        raise ValueError('No hay imágenes para predecir')
    if not (Path(model_dir) / 'modelo.pt').is_file():
        raise ValueError(f'No existe {Path(model_dir) / "modelo.pt"}')
    device = pick_device(device)
    artifact, model = load_model(model_dir, device)
    images = np.stack([load_image(path, artifact['image_size']) for path in paths])
    scores = score(artifact, model, images, np.arange(len(paths)), device)
    threshold = artifact['threshold']
    return [{'image': str(path), 'score': float(value), 'predicted': int(value >= threshold)}
            for path, value in zip(paths, scores)], artifact


def as_json(model_dir, rows, artifact):
    """Resultado listo para otra aplicación: un objeto por imagen y los datos del modelo usado."""
    target = artifact['target']
    return {'modelo': str(model_dir), 'hallazgo': target, 'umbral': round(float(artifact['threshold']), 6),
            'predicciones': [{'imagen': row['image'], 'puntaje': round(row['score'], 6),
                              'positivo': bool(row['predicted']),
                              'clase': target if row['predicted'] else f'sin {target}'} for row in rows]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('imagenes', type=Path, nargs='+', help='PNG, JPEG o TIFF')
    parser.add_argument('--modelo', type=Path, default=DEFAULT_MODEL, help=f'Carpeta con modelo.pt (por defecto {DEFAULT_MODEL})')
    parser.add_argument('--json', action='store_true', help='Imprime el resultado como JSON')
    parser.add_argument('--salida', type=Path, help='CSV opcional con un puntaje por imagen')
    parser.add_argument('--dispositivo', default='auto', help='auto, cpu, mps o cuda')
    args = parser.parse_args()
    try:
        rows, artifact = predict(args.modelo, args.imagenes, args.dispositivo)
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        raise SystemExit(1) from None
    if args.json:
        print(json.dumps(as_json(args.modelo, rows, artifact), indent=2, ensure_ascii=False))
    else:
        target = artifact['target']
        print(f'{args.modelo.name} · umbral {artifact["threshold"]:.3f} (elegido en validación)')
        for row in rows:
            print(f'{Path(row["image"]).name}  {row["score"]:.3f}  {target if row["predicted"] else "sin " + target}')
    if args.salida:
        write_csv(args.salida, rows)


if __name__ == '__main__':
    main()
