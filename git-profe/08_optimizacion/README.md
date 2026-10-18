# Clase 8 - Optimización: búsqueda local y espacios continuos

Se aborda la resolución de problemas de **optimización** mediante algoritmos de búsqueda local, usando el **Sudoku** como caso de estudio: se modela el problema (estados, vecinos y función de costo) y se resuelve con distintos algoritmos, comparando su desempeño. Al final, se ve cómo cambia el enfoque cuando el espacio de búsqueda es **continuo**.

## Notebooks

- [`01_resolviendo_sudokus.ipynb`](01_resolviendo_sudokus.ipynb) — definición del problema: coordenadas de las celdas y unidades del Sudoku, representación del estado, estados al azar, verificación de solución, generación de vecinos y función de costo (basado en el trabajo de Peter Norvig).
- [`02_sudoku_gradiente_descendente.ipynb`](02_sudoku_gradiente_descendente.ipynb) — gradiente descendente discreto y su variante estocástica; cómo moverse en mesetas.
- [`03_sudoku_simulated_annealing.ipynb`](03_sudoku_simulated_annealing.ipynb) — Simulated Annealing: aceptar (con cierta probabilidad) movimientos peores para escapar de óptimos locales.
- [`04_sudoku_local_beam_search.ipynb`](04_sudoku_local_beam_search.ipynb) — Local Beam Search: en vez de un único estado inicial, se mantienen varios estados a la vez.
- [`05_sudoku_algoritmo_genetico.ipynb`](05_sudoku_algoritmo_genetico.ipynb) — Algoritmos Genéticos: cromosoma, reproducción y mutación aplicados al Sudoku.
- [`06_busqueda_continua.ipynb`](06_busqueda_continua.ipynb) — búsqueda en espacios continuos: gradiente descendente usando el gradiente calculado.

## Ejercicio

- [`ejercicios/`](ejercicios/) — evaluación práctica: implementar Simulated Annealing para resolver el problema de las N reinas. Ver su [README](ejercicios/README.md).

## Código de apoyo

Las notebooks importan estos módulos directamente (tienen que quedar en la misma carpeta que las notebooks):

- [`sudoku_stuff.py`](sudoku_stuff.py) — definición del problema: celdas, unidades, estados, vecinos, verificación de solución y función de costo.
- [`search_methods.py`](search_methods.py) — los algoritmos de búsqueda aplicados al Sudoku (gradiente descendente, Simulated Annealing, Local Beam Search y algoritmo genético).
- [`genetic.py`](genetic.py) — herramientas del algoritmo genético: cromosoma, reproducción y mutación.
- [`processing.py`](processing.py) — ejecuta muchas búsquedas en paralelo (`multiprocessing`) con barra de progreso (`tqdm`), para comparar qué tan seguido cada algoritmo encuentra la solución.
- [`img/`](img/) — imágenes de los Sudokus usados en las notebooks.

## Notas

- Las notebooks `02` a `05` lanzan 500 búsquedas en paralelo usando todos los núcleos de la máquina, y **pueden tardar bastante**. Como referencia, en una máquina de 24 núcleos la ejecución completa tardó: `02` ≈ 20 min, `03` ≈ 1,5 min, `04` ≈ 6,5 min y `05` ≈ 15 min (con menos núcleos va a tardar más). Para probar más rápido, bajá el parámetro `max_iterations` de `parallel_sudoku_search`.
- Las barras de progreso (`tqdm.notebook`) necesitan `ipywidgets` (ya incluido en las dependencias del repositorio).

## Fuentes de datos

No hay datasets: los Sudokus se definen en las propias notebooks (ver [`img/`](img/) para su representación gráfica).

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
