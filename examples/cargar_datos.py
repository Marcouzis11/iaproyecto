"""Inspecciona los arrays preparados. Ejecutar desde la raíz del repositorio.

python examples/cargar_datos.py --data data/processed/mis_radiografias_v1
"""

import argparse
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    args = parser.parse_args()
    for split in ('train', 'val', 'test'):
        images = np.load(args.data / f'X_{split}.npy', mmap_mode='r', allow_pickle=False)
        labels = np.load(args.data / f'y_{split}.npy', allow_pickle=False)
        print(f'{split}: X={images.shape}, dtype={images.dtype}; y={labels.shape}')
        # Para un clasificador tabular de sklearn:
        vectors = images.reshape(len(images), -1)
        print(f'  Vista como vectores para sklearn: {vectors.shape}')
        # Para una CNN: images[:, None, :, :] -> N,1,H,W (canal primero).
        # No concatenar estos conjuntos para ajustar transformaciones o modelos.
        del vectors, images


if __name__ == '__main__':
    main()
