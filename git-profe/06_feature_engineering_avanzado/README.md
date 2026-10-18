# Clase 6 - Feature engineering y EDA avanzado

## Notebooks

- [`01_discretizacion.ipynb`](01_discretizacion.ipynb) — convertir una variable numérica continua en categorías: intervalos de igual amplitud, de igual frecuencia, con K-means (`KBinsDiscretizer`), y con puntos de corte manuales.
- [`02_normalizacion_estandarizacion.ipynb`](02_normalizacion_estandarizacion.ipynb) — normalización Min-Max vs. estandarización Z-score: qué cambia (media, varianza, covarianza) y qué se mantiene igual (correlación de Pearson).
- [`03_desbalance.ipynb`](03_desbalance.ipynb) — qué hacer cuando el target está desbalanceado: entropía de Shannon para medir el desbalance, oversampling con SMOTE y undersampling con `RandomUnderSampler`.
- [`04_tratamiento_datos_faltantes_avanzado.ipynb`](04_tratamiento_datos_faltantes_avanzado.ipynb) — imputación multivariada: KNN Imputer y MICE (Iterative Imputer), que usan el resto de las variables de cada fila para estimar el valor faltante.
- [`05_tratamiento_outliers_avanzado.ipynb`](05_tratamiento_outliers_avanzado.ipynb) — tratar outliers marcándolos como faltantes e imputándolos con KNN Imputer, en vez de con un valor estadístico fijo.
- [`06_eda_automatico.ipynb`](06_eda_automatico.ipynb) — generación automática de reportes EDA con `ydata-profiling` y `sweetviz` (incluye comparación entre train y test).
- [`07_eda_texto.ipynb`](07_eda_texto.ipynb) — EDA de texto (NLP): tamaño del corpus, frecuencia de palabras, limpieza de stopwords/puntuación, nube de palabras, sobre el corpus de noticias Reuters.
- [`08_eda_audio.ipynb`](08_eda_audio.ipynb) — EDA de audio: forma de onda, distribución de amplitudes y espectrogramas, sobre 4 archivos de audio de ejemplo.
- [`09_eda_imagenes.ipynb`](09_eda_imagenes.ipynb) — EDA de imágenes: visualización de muestras, histograma de intensidad de píxeles y distribución de clases, sobre el dataset CIFAR-10.

## Fuentes de datos

- `01` a `07` usan datasets remotos que se descargan solos la primera vez que se corren: Titanic y Penguins vía seaborn (se cachean en `~/seaborn-data`), el corpus Reuters vía `nltk.download(...)` en `07` (se cachea en `~/nltk_data`).
- `08_eda_audio.ipynb` usa 4 archivos de audio en [`audio/`](audio/) (de [Pixabay](https://pixabay.com/sound-effects/search/voice/), libres de derechos).
- `09_eda_imagenes.ipynb` descarga el dataset CIFAR-10 (~170 MB) la primera vez que se corre, vía `tensorflow.keras.datasets.cifar10` (se cachea en `~/.keras/datasets`).
- `06_eda_automatico.ipynb` genera reportes HTML/JSON en `reportes/` (no versionados — ver `.gitignore`).

## Dependencias más pesadas

Esta clase agrega varias librerías grandes: `tensorflow` (para `09`), `librosa` (para `08`), `ydata-profiling` y `sweetviz` (para `06`), `nltk` y `wordcloud` (para `07`). `uv pip install -e .` va a tardar bastante más que en las clases anteriores la primera vez.

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
