"""CLI: rx-verificar-datos data/processed/<carpeta> [--generar].

Comprueba que una carpeta preparada sea idéntica, byte a byte, a la que usó el equipo: compara el SHA-256 de cada
archivo con configs/<carpeta>.sha256. Así, quien recibe los datos por Drive sabe que entrena y evalúa con los
mismos arrays y la misma partición. La lista tiene el formato de sha256sum, así que también se verifica con
`shasum -a 256 -c` desde la carpeta. Con --generar se escribe la lista de una preparación nueva.
"""

import argparse
import hashlib
import sys
from pathlib import Path

DEFAULT_LISTS = Path('configs')


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def manifest_path(folder, lists=DEFAULT_LISTS):
    return Path(lists) / f'{Path(folder).name}.sha256'


def files_in(folder):
    """Archivos de la preparación, sin los ocultos del sistema (.DS_Store y similares)."""
    return sorted(p for p in Path(folder).iterdir() if p.is_file() and not p.name.startswith('.'))


def write_manifest(folder, path):
    path = Path(path)
    if path.exists():
        raise ValueError(f'{path} ya existe: la lista de una preparación no se pisa')
    files = files_in(folder)
    if not files:
        raise ValueError(f'{folder} no tiene archivos')
    path.write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in files), encoding='utf-8')
    return len(files)


def read_manifest(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'No existe {path}')
    expected = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            expected[name.lstrip('*')] = digest
    return expected


def verify(folder, path):
    """Lista de problemas (vacía si todo coincide): archivos que faltan o con otro contenido."""
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError(f'No existe la carpeta {folder}')
    problems = []
    for name, digest in read_manifest(path).items():
        file = folder / name
        if not file.is_file():
            problems.append(f'falta {name}')
        elif sha256(file) != digest:
            problems.append(f'{name} tiene otro contenido')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('carpeta', type=Path, help='Carpeta preparada, por ejemplo data/processed/nih_effusion_pa_modelo_b_v1')
    parser.add_argument('--lista', type=Path, help=f'Lista de SHA-256 (por defecto {DEFAULT_LISTS}/<carpeta>.sha256)')
    parser.add_argument('--generar', action='store_true', help='Escribir la lista en lugar de verificar')
    args = parser.parse_args()
    path = args.lista or manifest_path(args.carpeta)
    try:
        if args.generar:
            print(f'{path}: {write_manifest(args.carpeta, path)} archivos')
            return
        problems = verify(args.carpeta, path)
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        raise SystemExit(1) from None
    for problem in problems:
        print(f'  {problem}')
    if problems:
        print(f'{args.carpeta} NO coincide con {path}', file=sys.stderr)
        raise SystemExit(1)
    print(f'{args.carpeta} coincide con {path}: {len(read_manifest(path))} archivos idénticos')


if __name__ == '__main__':
    main()
