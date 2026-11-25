"""CLI: rx-descargar-pesos [modelo ...]. Baja los pesos de A, control y C del release pesos-v1 de GitHub.

El modelo final (B) viene en el repositorio. Los otros tres pesan 28 MB cada uno y se publican aparte para
no hacer pesado cada clon. Cada archivo se verifica con su SHA-256 antes de dejarlo en models/<modelo>/modelo.pt;
con eso, rx-predecir --modelo y rx-probar --modelo funcionan con cualquiera de los cuatro.
"""

import argparse
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from rx_torax.data.checksums import sha256

RELEASE = 'https://github.com/Marcouzis11/iaproyecto/releases/download/pesos-v1'
DEFAULT_MODELS = Path('models')
# SHA-256 de cada modelo.pt, el mismo archivo que generó los report.json versionados.
WEIGHTS = {
    'modelo_a_densenet121_v1': '38a0f99199e53d4a72803259205ec98aa28a50b00d9e99a8f11b8cf29ab3039f',
    'modelo_control_v2_densenet121': '1c23c6aa85ee3c3f5e49fafa43a6211baf8b7c39794b4a896116f7345fdd3bf4',
    'modelo_c_v2_densenet121': '2aab1a55ade2692c72c9c1c50922765e2936b2e61981a9ed34e131dce6e8f01e',
}


def download(name, models=DEFAULT_MODELS, source=RELEASE):
    """Deja models/<name>/modelo.pt verificado. Devuelve la ruta y si hizo falta bajarlo."""
    if name not in WEIGHTS:
        raise ValueError(f'No hay pesos publicados para {name}. Opciones: {", ".join(WEIGHTS)}')
    target = Path(models) / name / 'modelo.pt'
    if target.is_file():
        if sha256(target) == WEIGHTS[name]:
            return target, False
        raise ValueError(f'{target} ya existe y no es el publicado; borralo si querés reemplazarlo')
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name('modelo.pt.parcial')
    try:
        with urllib.request.urlopen(f'{source}/{name}.pt', timeout=120) as response, partial.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        if sha256(partial) != WEIGHTS[name]:
            raise ValueError(f'{name}: lo bajado no coincide con su SHA-256; probá de nuevo')
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)
    return target, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nombres', nargs='*', default=list(WEIGHTS), metavar='modelo',
                        help=f'Por defecto, los tres: {", ".join(WEIGHTS)}')
    parser.add_argument('--modelos', type=Path, default=DEFAULT_MODELS, help=f'Carpeta de modelos (por defecto {DEFAULT_MODELS})')
    args = parser.parse_args()
    for name in args.nombres:
        try:
            target, downloaded = download(name, args.modelos)
        except (ValueError, OSError, urllib.error.URLError) as error:
            print(f'error: {error}', file=sys.stderr)
            raise SystemExit(1) from None
        print(f'{target}  {"bajado y verificado" if downloaded else "ya estaba, verificado"}')


if __name__ == '__main__':
    main()
