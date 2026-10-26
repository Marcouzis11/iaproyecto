"""Lectura de PNG/JPEG y TIFF de un solo frame, sin recorte anatómico."""

import hashlib
import warnings
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


def read_image(path: Path):
    """Devuelve grises float32 [0,1], hash de píxeles y características originales.

    La escala depende del formato de almacenamiento, nunca del máximo de cada
    imagen. No interpreta DICOM, windowing, MONOCHROME1 ni metadatos clínicos.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as original:
            if original.format not in {"PNG", "JPEG", "TIFF"}:
                raise ValueError("Formato no admitido: usar PNG, JPEG o TIFF")
            if getattr(original, "n_frames", 1) != 1:
                raise ValueError("Imagen multiframe no admitida")
            image = ImageOps.exif_transpose(original)
            mode = image.mode
            if mode == "RGB":
                pixels = np.asarray(image.convert("L"))
                scale = 255.0
            elif mode == "RGBA":
                # Algunas PNG de NIH vienen en RGBA con alfa constante; solo se aceptan si son opacas.
                if np.asarray(image.getchannel("A")).min() < 255:
                    raise ValueError("Imagen RGBA con transparencia no admitida")
                pixels = np.asarray(image.convert("RGB").convert("L"))
                scale = 255.0
            elif mode == "L":
                pixels = np.asarray(image)
                scale = 255.0
            elif mode.startswith("I;16") or (mode == "I" and original.format == "PNG"):
                pixels = np.asarray(image)
                if pixels.min() < 0 or pixels.max() > 65535:
                    raise ValueError("Valores fuera del rango unsigned de 16 bits")
                scale = 65535.0
            else:
                raise ValueError(f"Modo {mode} no admitido; convertir de forma explícita")
            fingerprint = hashlib.sha256()
            fingerprint.update(str((pixels.shape, scale)).encode())
            fingerprint.update(np.asarray(pixels, dtype="<u2").tobytes())
            info = {"width": image.width, "height": image.height, "mode": mode,
                    "intensity_scale": int(scale), "pixel_hash": fingerprint.hexdigest()}
            return pixels.astype(np.float32) / scale, info


def transform(path: Path, size: int, expected_hash=None):
    """Redimensiona sin deformar y centra con padding negro. Salida (H,W)."""
    pixels, info = read_image(path)
    if expected_hash is not None and info['pixel_hash'] != expected_hash:
        raise ValueError(f"La imagen cambió después de la auditoría: {path}")
    height, width = pixels.shape
    factor = size / max(height, width)
    new_size = (max(1, round(width * factor)), max(1, round(height * factor)))
    resized = np.asarray(Image.fromarray(pixels).resize(new_size, Image.Resampling.BILINEAR))
    result = np.zeros((size, size), dtype=np.float32)
    x, y = (size - new_size[0]) // 2, (size - new_size[1]) // 2
    result[y:y + new_size[1], x:x + new_size[0]] = resized
    return result
