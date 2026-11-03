"""CLI: rx-predecir --modelo models/modelo_b_densenet121_v1 imagen.png [otra.png ...].

Aplica la misma transformación que la preparación y el umbral guardado en modelo.pt, elegido en validación.
El modelo se entrenó con radiografías PA de NIH: con otras vistas u otras imágenes el puntaje no significa nada.
"""

import argparse
from pathlib import Path

import numpy as np

from rx_torax.evaluation.evaluate import load_model, score
from rx_torax.preprocessing.images import transform
from rx_torax.training.train import pick_device, write_csv


def load_image(path, size):
    try:
        return transform(path, size)
    except (OSError, ValueError) as error:
        raise ValueError(f'{path}: {error}') from error


def predict(model_dir, paths, device='auto'):
    paths = [Path(path) for path in paths]
    if not paths:
        raise ValueError('No hay imágenes para predecir')
    device = pick_device(device)
    artifact, model = load_model(model_dir, device)
    images = np.stack([load_image(path, artifact['image_size']) for path in paths])
    scores = score(artifact, model, images, np.arange(len(paths)), device)
    threshold = artifact['threshold']
    return [{'image': str(path), 'score': float(value), 'predicted': int(value >= threshold)}
            for path, value in zip(paths, scores)], artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('imagenes', type=Path, nargs='+', help='PNG, JPEG o TIFF')
    parser.add_argument('--modelo', type=Path, required=True)
    parser.add_argument('--salida', type=Path, help='CSV opcional con un puntaje por imagen')
    parser.add_argument('--dispositivo', default='auto')
    args = parser.parse_args()
    rows, artifact = predict(args.modelo, args.imagenes, args.dispositivo)
    target = artifact['target']
    print(f'{args.modelo.name} · umbral {artifact["threshold"]:.3f} (elegido en validación)')
    for row in rows:
        print(f'{Path(row["image"]).name}  {row["score"]:.3f}  {target if row["predicted"] else "sin " + target}')
    if args.salida:
        write_csv(args.salida, rows)


if __name__ == '__main__':
    main()
