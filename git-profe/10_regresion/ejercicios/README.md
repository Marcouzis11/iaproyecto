# Ejercicio - Dataset Swiss

## Descripción del problema

En este ejercicio deben implementar dos modelos de **regresión** para resolver un problema supervisado utilizando el conjunto de datos **Swiss**.

El dataset Swiss es un conjunto de datos clásico que contiene información socioeconómica y demográfica de 47 provincias suizas a fines del siglo XIX (tasa de fertilidad, porcentaje de educación, proporción de católicos, entre otras). El objetivo es predecir la variable `Fertility` a partir del resto de las variables.

## Instrucciones de entrega

- [`01_ejercicio_swiss_regresion.ipynb`](01_ejercicio_swiss_regresion.ipynb) — notebook a completar. Es **obligatorio** completar únicamente las secciones indicadas (marcadas con `##### COMPLETAR AQUI LO PEDIDO`), sin agregar contenido adicional.
- [`swiss.csv`](swiss.csv) — el dataset.

La notebook ya trae la carga de datos y el split train/test (50/50, dado que son pocas observaciones). Hay que completar dos partes:

1. **Regresión lineal múltiple**: escalar los atributos (`StandardScaler`), entrenar con todos los atributos, predecir sobre test y calcular MAE, MSE y R².
2. **Modelo con regularización**: usar `LassoCV` y `RidgeCV` para buscar automáticamente el mejor hiperparámetro `alpha` por validación cruzada.

## Cómo resolverla

Con el entorno del repositorio ya configurado (ver [Quick start](../../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir la notebook. Podés usar como referencia [`../04_regularizacion.ipynb`](../04_regularizacion.ipynb), donde se aplican Ridge y Lasso.
