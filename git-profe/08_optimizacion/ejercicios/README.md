# Ejercicio - N reinas

## Descripción del problema

En este ejercicio deben implementar el algoritmo de **Simulated Annealing** para resolver el problema de las **N reinas**.

El problema de las N reinas es un clásico desafío en informática que consiste en colocar $N$ reinas sobre un tablero de ajedrez de tamaño $N \times N$ de manera que ninguna reina pueda atacar a otra.

## Instrucciones de entrega

- [`01_ejercicio_n_reinas.ipynb`](01_ejercicio_n_reinas.ipynb) — notebook a completar. Es **obligatorio** completar únicamente las secciones indicadas (marcadas con `TODO` / `<<ESCRIBE AQUÍ>>`), sin agregar contenido adicional.

La notebook ya trae implementados el estado, la generación de vecinos, la función de costo, la visualización del tablero y el algoritmo de gradiente descendente (*hill climbing*). Lo que tienen que completar es la función `simulated_annealing`, elegir los valores de `initial_temp` y `cooling_rate` (las celdas que ejecutan el algoritmo fallan con `NameError` hasta que los definan) y contar en cuántas de 5 ejecuciones se encontró la solución.

## Cómo resolverla

Con el entorno del repositorio ya configurado (ver [Quick start](../../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir la notebook. Podés usar como referencia [`../03_sudoku_simulated_annealing.ipynb`](../03_sudoku_simulated_annealing.ipynb), donde se implementa Simulated Annealing para resolver Sudokus.
