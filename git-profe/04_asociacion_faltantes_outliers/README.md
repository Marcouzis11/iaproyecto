# Clase 4 - Medidas de asociación, datos faltantes y outliers

## Notebooks

- [`01_medidas_asociacion.ipynb`](01_medidas_asociacion.ipynb) — medidas de asociación entre variables más allá de la correlación de Pearson: coeficiente Phi (binaria-binaria), punto biserial (numérica-binaria), V de Cramér (categórica-categórica), Tau-b de Kendall (numérica-ordinal) y Eta cuadrado (numérica-categórica).
- [`02_datos_faltantes_outliers.ipynb`](02_datos_faltantes_outliers.ipynb) — identificación y visualización de datos faltantes con `missingno` (barras, matriz, heatmap de correlación de nulos, dendrograma), análisis de sus posibles causas (MCAR / MAR / MNAR), y detección de outliers con dos métodos: rango intercuartil (IQR) y desviación estándar.
- [`03_eda_ejemplo_smn.ipynb`](03_eda_ejemplo_smn.ipynb) — caso práctico completo que aplica todo lo anterior sobre datos reales del Servicio Meteorológico Nacional: EDA de variables categóricas (con entropía) y numéricas, análisis de datos faltantes variable por variable, y análisis de outliers.

## Fuentes de datos

- `01_medidas_asociacion.ipynb` y `02_datos_faltantes_outliers.ipynb` usan el dataset Titanic incluido en seaborn (`sns.load_dataset('titanic')`): no requieren ningún archivo local, pero sí conexión a internet la primera vez que se corren (seaborn lo descarga y lo cachea en `~/seaborn-data`).
- `03_eda_ejemplo_smn.ipynb` usa [`../datasets/smn_historico.csv`](../datasets/smn_historico.csv): estadísticas climáticas normales (1991-2020) y temperaturas del último año por estación meteorológica, del [Servicio Meteorológico Nacional Argentino](https://www.smn.gob.ar/descarga-de-datos).

Del mismo origen (SMN) quedan estos datasets adicionales en [`../datasets/`](../datasets/), de referencia — ninguna notebook los usa todavía:

| Archivo | Contenido |
|---|---|
| `smn_estaciones.txt` | Listado de estaciones meteorológicas: nombre, provincia, latitud, longitud, altura, número y NroOACI. |
| `smn_estadisticas_normales_1991-2020.txt` | Estadísticas climatológicas normales, período 1991-2020 (texto con metadata y notas del SMN). |
| `smn_registro_temperatura_365d.txt` | Temperatura máxima y mínima diaria por estación, últimos 365 días (formato de ancho fijo). |
| `smn_ultimo_anio.csv` | Igual que el anterior pero en CSV: `fecha`, `temp_max`, `temp_min`, `estación`. |

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
