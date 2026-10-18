# Computer Vision

Introducción práctica a OpenCV: desde representar una imagen como una matriz de números hasta operaciones típicas de visión por computadora sobre imágenes binarias.

## Notebooks

- [`01_introduccion_opencv.ipynb`](01_introduccion_opencv.ipynb) — qué es OpenCV y cómo instalarlo, cómo una imagen es ni más ni menos que una matriz de números (con y sin color), y los fundamentos de la librería: lectura de imágenes, separación de canales de color, y anotaciones (líneas, rectángulos, círculos, elipses, polígonos y texto).
- [`02_imagenes_binarias_morfologia.ipynb`](02_imagenes_binarias_morfologia.ipynb) — conversión a escala de grises, umbralización (simple, adaptativa y de Otsu), transformaciones geométricas (traslación, rotación, escalado, corrección de perspectiva) y operaciones morfológicas (erosión, dilatación, apertura, cierre, gradiente).

## Fuentes de datos

Todas las imágenes usadas están en [`img/`](img/) — fotos y recursos de ejemplo, sin dependencias externas ni descargas.

## Notas

- Al ejecutar `01_introduccion_opencv.ipynb` se genera `modificada.png` en esta carpeta (una imagen de ejemplo, guardada para mostrar `cv2.imwrite`). No se versiona — ver `.gitignore`.
- La corrección de perspectiva en `02_imagenes_binarias_morfologia.ipynb` originalmente se hacía seleccionando 4 puntos con clics del mouse (`cv2.setMouseCallback`), algo que solo funciona en una ventana nativa, no dentro de una notebook. Acá los puntos quedan fijos de antemano — está aclarado en la propia notebook.

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
