# Clase 9 - Aprendizaje automático

Introducción práctica a **scikit-learn**, la librería más usada de Machine Learning en Python, recorriendo el ciclo de vida completo de un modelo sobre el dataset Iris (incluido en la propia librería): preprocesamiento, separación en train/test, entrenamiento, evaluación, predicción, y guardado/carga del modelo entrenado.

## Notebook

- [`01_scikit_learn.ipynb`](01_scikit_learn.ipynb) — ciclo de vida de un modelo de ML con scikit-learn:
  - **Preprocesamiento**: escalado de variables con `StandardScaler`.
  - **Separación del dataset**: `train_test_split`.
  - **Entrenamiento**: `KNeighborsClassifier` (K vecinos más cercanos).
  - **Evaluación**: `accuracy_score`.
  - **Predicción** sobre datos nuevos, y guardado/carga del modelo entrenado con `joblib`.

## Fuentes de datos

Usa el dataset **Iris** incluido en scikit-learn (`sklearn.datasets.load_iris()`): no requiere descarga ni archivos locales, está empaquetado con la librería.

## Notas

- Al ejecutar la notebook se genera `modelo.pkl` en esta carpeta (el modelo entrenado, serializado con `joblib`). No se versiona — ver `.gitignore`.

## Cómo abrirla

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir la notebook.
