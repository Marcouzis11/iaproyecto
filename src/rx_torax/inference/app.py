"""rx-probar: página local para probar el modelo subiendo radiografías desde el navegador.

Levanta un servidor solo en esta computadora (127.0.0.1) con la misma transformación y el mismo umbral
que rx-predecir. Además del puntaje devuelve un mapa de calor (Grad-CAM) con las zonas que más empujan
el puntaje hacia derrame: sirve para ver dónde mira el modelo, no es una segmentación ni un diagnóstico.
"""

import argparse
import base64
import io
import json
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import torch
from matplotlib import colormaps
from PIL import Image, UnidentifiedImageError
from torch.nn import functional as F

from rx_torax.evaluation.evaluate import load_model
from rx_torax.inference.predict import DEFAULT_MODEL
from rx_torax.preprocessing.images import transform
from rx_torax.training.model import to_input
from rx_torax.training.train import pick_device

PAGINA = Path(__file__).with_name('pagina.html')
MAX_BYTES = 40 * 1024 * 1024
ERRORES_DE_IMAGEN = (ValueError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning)


def png_base64(rgb):
    """Array H,W,3 en [0, 1] a data URL PNG, para mostrarlo directo en la página."""
    buffer = io.BytesIO()
    Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8)).save(buffer, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')


def superponer(imagen, mapa, opacidad=0.55):
    """Pinta el mapa de calor (0 a 1) sobre la radiografía en grises; lo frío queda transparente."""
    base = np.repeat(imagen[..., None], 3, axis=2)
    color = colormaps['inferno'](mapa)[..., :3]
    alfa = (opacidad * mapa)[..., None]
    return base * (1 - alfa) + color * alfa


class Analizador:
    """Carga el modelo una vez y analiza imágenes de a una."""

    def __init__(self, model_dir=DEFAULT_MODEL, device='auto'):
        model_dir = Path(model_dir)
        if not (model_dir / 'modelo.pt').is_file():
            raise ValueError(f'No existe {model_dir / "modelo.pt"}')
        self.model_dir = model_dir
        self.device = pick_device(device)
        self.artifact, self.model = load_model(model_dir, self.device)
        self.lock = threading.Lock()

    def info(self):
        return {'modelo': self.model_dir.name, 'hallazgo': self.artifact['target'],
                'umbral': round(float(self.artifact['threshold']), 6), 'tamaño': int(self.artifact['image_size'])}

    def puntaje_y_mapa(self, imagen):
        """Mismo cálculo que DenseNet121.forward, guardando las activaciones de la última capa convolucional."""
        batch = torch.from_numpy(imagen[None]).to(self.device)
        entrada = to_input(batch, self.artifact['train_mean'], self.artifact['train_std'])
        activaciones = F.relu(self.model.features(entrada))
        logit = self.model.classifier(torch.flatten(F.adaptive_avg_pool2d(activaciones, (1, 1)), 1)).squeeze()
        (gradiente,) = torch.autograd.grad(logit, activaciones)
        pesos = gradiente.mean(dim=(2, 3), keepdim=True)
        mapa = torch.relu((pesos * activaciones).sum(dim=1)).squeeze(0).detach().cpu().numpy()
        return float(torch.sigmoid(logit).item()), mapa

    def analizar(self, datos):
        """Bytes de una imagen PNG, JPEG o TIFF a puntaje, clase, imagen de entrada y mapa de calor."""
        tamaño = int(self.artifact['image_size'])
        try:
            imagen = transform(io.BytesIO(datos), tamaño)
        except UnidentifiedImageError:
            raise ValueError('El archivo no es una imagen PNG, JPEG o TIFF') from None
        with self.lock:
            puntaje, mapa = self.puntaje_y_mapa(imagen)
        mapa = np.asarray(Image.fromarray(mapa.astype(np.float32)).resize((tamaño, tamaño), Image.Resampling.BILINEAR))
        mapa = mapa / mapa.max() if mapa.max() > 0 else mapa
        umbral = float(self.artifact['threshold'])
        hallazgo = self.artifact['target']
        positivo = puntaje >= umbral
        return {'puntaje': round(puntaje, 6), 'positivo': bool(positivo),
                'clase': hallazgo if positivo else f'sin {hallazgo}', 'umbral': round(umbral, 6),
                'entrada': png_base64(np.repeat(imagen[..., None], 3, axis=2)),
                'mapa': png_base64(superponer(imagen, mapa))}


class Manejador(BaseHTTPRequestHandler):
    analizador = None
    pagina = b''

    def responder(self, estado, cuerpo, tipo='application/json; charset=utf-8'):
        if not isinstance(cuerpo, bytes):
            cuerpo = json.dumps(cuerpo, ensure_ascii=False).encode('utf-8')
        self.send_response(estado)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(cuerpo)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.responder(HTTPStatus.OK, self.pagina, 'text/html; charset=utf-8')
        elif self.path == '/api/modelo':
            self.responder(HTTPStatus.OK, self.analizador.info())
        else:
            self.responder(HTTPStatus.NOT_FOUND, {'error': 'No existe'})

    def do_POST(self):
        if self.path != '/api/predecir':
            self.responder(HTTPStatus.NOT_FOUND, {'error': 'No existe'})
            return
        largo = int(self.headers.get('Content-Length') or 0)
        if largo <= 0:
            self.responder(HTTPStatus.BAD_REQUEST, {'error': 'No llegó ninguna imagen'})
            return
        if largo > MAX_BYTES:
            self.responder(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {'error': 'La imagen pesa más de 40 MB'})
            return
        datos = self.rfile.read(largo)
        try:
            resultado = self.analizador.analizar(datos)
        except ERRORES_DE_IMAGEN as error:
            self.responder(HTTPStatus.BAD_REQUEST, {'error': str(error)})
            return
        self.responder(HTTPStatus.OK, resultado)

    def log_message(self, formato, *args):
        pass


def crear_servidor(analizador, puerto=8765, host='127.0.0.1'):
    """Servidor listo para serve_forever(); con puerto 0 el sistema elige uno libre."""
    manejador = type('ManejadorDelModelo', (Manejador,), {'analizador': analizador, 'pagina': PAGINA.read_bytes()})
    return ThreadingHTTPServer((host, puerto), manejador)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo', type=Path, default=DEFAULT_MODEL, help=f'Carpeta con modelo.pt (por defecto {DEFAULT_MODEL})')
    parser.add_argument('--puerto', type=int, default=8765, help='Puerto local (por defecto 8765)')
    parser.add_argument('--dispositivo', default='auto', choices=['auto', 'cpu', 'mps', 'cuda'], help='Dónde corre el modelo')
    parser.add_argument('--no-abrir', action='store_true', help='No abrir el navegador automáticamente')
    args = parser.parse_args()
    try:
        analizador = Analizador(args.modelo, args.dispositivo)
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        raise SystemExit(1) from None
    try:
        servidor = crear_servidor(analizador, args.puerto)
    except OSError as error:
        print(f'error: no se pudo usar el puerto {args.puerto} ({error}). Probá con --puerto y otro número.', file=sys.stderr)
        raise SystemExit(1) from None
    url = f'http://127.0.0.1:{servidor.server_port}/'
    print(f'Página lista en {url}  ·  modelo {args.modelo.name}, umbral {analizador.artifact["threshold"]:.3f}  ·  Ctrl+C para cerrar')
    if not args.no_abrir:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nPágina cerrada.')
    finally:
        servidor.server_close()


if __name__ == '__main__':
    main()
