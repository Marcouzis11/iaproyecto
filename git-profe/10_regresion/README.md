# Clase 10 - Regresión

Modelos de regresión con scikit-learn: desde una regresión lineal simple hasta regularización (Ridge/Lasso) y funciones base no lineales, con selección de modelo y evaluación en cada paso.

## Notebooks

- [`01_regresion_simple.ipynb`](01_regresion_simple.ipynb) — regresión lineal simple: concentración de un fármaco en sangre en función del tiempo. Entrenamiento, evaluación y guardado/carga del modelo con `joblib`.
- [`02_regresion_multiple.ipynb`](02_regresion_multiple.ipynb) — regresión lineal múltiple: predicción de ganancias de startups a partir de varios atributos (incluida una variable categórica, con `OneHotEncoder` dentro de un `Pipeline`).
- [`03_seleccion_de_modelo.ipynb`](03_seleccion_de_modelo.ipynb) — ¿se puede lograr un rendimiento similar con menos atributos? Comparación entre el modelo completo de `02` y una versión simplificada.
- [`04_regularizacion.ipynb`](04_regularizacion.ipynb) — regresión Ridge y Lasso para controlar el sobreajuste, como alternativa a la selección manual de atributos de `03`.
- [`05_regresion_no_lineal.ipynb`](05_regresion_no_lineal.ipynb) — regresión con funciones base para modelar relaciones no lineales.

## Ejercicio

- [`ejercicios/`](ejercicios/) — evaluación práctica: regresión lineal múltiple y regresión regularizada (Ridge/Lasso) sobre el dataset Swiss. Ver su [README](ejercicios/README.md).

## Fuentes de datos

En [`datasets/`](datasets/):

| Archivo | Contenido | Usado en |
|---|---|---|
| `drug.csv` | Concentración de un fármaco en sangre a lo largo del tiempo. | `01` |
| `50_Startups.csv` | Gastos (I+D, administración, marketing), estado y ganancia de 50 startups. | `02`, `03`, `04` |
| `Synthetic_Puromycin.csv` | Datos sintéticos de velocidad de reacción enzimática según concentración de sustrato. | `05` |

## Notas

- Al ejecutar las notebooks se generan varios `.pkl` (modelos entrenados, serializados con `joblib`) en esta carpeta. No se versionan — ver `.gitignore`.
- `03_seleccion_de_modelo.ipynb` carga el modelo guardado por `02_regresion_multiple.ipynb` (`reg_completo_50_startup.pkl`): hay que correr `02` al menos una vez antes que `03`.

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
