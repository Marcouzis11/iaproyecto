# Clase 3 - Análisis exploratorio de datos (EDA)

## Notebooks

- [`01_correlacion.ipynb`](01_correlacion.ipynb) — qué mide (y qué no) la correlación: comparación de Pearson, Spearman y Kendall sobre relaciones lineales, monótonas y no monótonas, con datos sintéticos.
- [`02_eda_titanic.ipynb`](02_eda_titanic.ipynb) — EDA completo sobre el dataset Titanic: estadística descriptiva (tendencia central, dispersión, forma), exploración de variables categóricas, y relaciones entre variables (correlación, tablas de contingencia, pairplot, violin/box/strip/swarm plots).

## Fuentes de datos

- `01_correlacion.ipynb` no usa datasets: trabaja con datos sintéticos generados en la propia notebook.
- `02_eda_titanic.ipynb` usa el dataset Titanic incluido en seaborn (`sns.load_dataset('titanic')`): no requiere ningún archivo local, pero sí conexión a internet la primera vez que se corre (seaborn lo descarga y lo cachea en `~/seaborn-data`).

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
