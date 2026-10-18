# Clase 5 - Procesamiento y limpieza de datos

## Notebooks

- [`01_split_y_stratify.ipynb`](01_split_y_stratify.ipynb) — split de un dataset en train/test con `train_test_split`, y por qué usar `stratify` cuando el target está desbalanceado.
- [`02_tratamiento_datos_faltantes.ipynb`](02_tratamiento_datos_faltantes.ipynb) — qué hacer con los datos faltantes: eliminación (filas, columnas, por umbral) e imputación (constante, valores estadísticos, forward/backward fill para series temporales).
- [`03_tratamiento_outliers.ipynb`](03_tratamiento_outliers.ipynb) — estrategias de tratamiento de outliers: eliminación, transformación logarítmica, imputación con valores estadísticos, y segmentación (marcarlos como categoría aparte).
- [`04_codificacion.ipynb`](04_codificacion.ipynb) — técnicas de codificación de variables categóricas: One-Hot, Binary, Ordinal, Hashing, Frequency, Target (Mean) y Cyclic encoding, más Label encoding para el target.

## Fuentes de datos

Todas las notebooks usan los datasets Titanic y Flights incluidos en seaborn (`sns.load_dataset(...)`): no requieren ningún archivo local, pero sí conexión a internet la primera vez que se corren (seaborn los descarga y los cachea en `~/seaborn-data`).

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
