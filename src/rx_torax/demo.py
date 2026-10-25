"""Genera imágenes geométricas SINTÉTICAS para probar la ejecución, no la IA."""

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image


def generate(output, patients=60):
    output = Path(output)
    if output.exists():
        raise ValueError(f'La carpeta ya existe: {output}')
    output.mkdir(parents=True)
    (output / 'images').mkdir()
    rng = np.random.default_rng(123)
    records = []
    for patient in range(patients):
        for study in range(2):
            image = rng.integers(0, 256, size=(48, 40), dtype=np.uint8)
            path = f'images/p{patient:03d}_{study}.png'
            Image.fromarray(image).save(output / path)
            records.append({'image_path': path, 'patient_id': f'p{patient:03d}',
                            'target': patient % 2, 'view': 'PA'})
    with (output / 'metadata.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    (output / 'SINTETICO.txt').write_text('Datos artificiales de prueba. No son radiografías.\n', encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='data/raw/demo_sintetica')
    args = parser.parse_args()
    try:
        print(generate(args.output).resolve())
    except (ValueError, OSError) as error:
        parser.exit(2, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
