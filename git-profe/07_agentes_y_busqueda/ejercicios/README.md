# Ejercicio - Torre de Hanoi

## Descripción del problema

En este ejercicio deben implementar un algoritmo de búsqueda que **no sea** Búsqueda Primero en Anchura (BFS) para resolver el problema de la Torre de Hanoi.

## Rúbrica de evaluación

La nota máxima depende del algoritmo que elijan implementar:

| Algoritmo de búsqueda | Condición / heurística | Nota máxima |
| :--- | :--- | :---: |
| Búsqueda Primero en Profundidad (DFS) | - | **6** |
| Búsqueda de Costo Uniforme (UCS) | - | **6** |
| Búsqueda de Profundidad Limitada con Profundidad Iterativa | - | **7** |
| Búsqueda Voraz (Greedy) | Heurística dada (ver [heurísticas](../heuristicas_torre_de_hanoi.md)) | **8** |
| Búsqueda Voraz (Greedy) | Heurística propia | **9** |
| Búsqueda A* | Heurística dada (ver [heurísticas](../heuristicas_torre_de_hanoi.md)) | **9** |
| Búsqueda A* | Heurística propia | **10** |

## Instrucciones de entrega

- [`01_ejercicio_torre_de_hanoi.ipynb`](01_ejercicio_torre_de_hanoi.ipynb) — notebook a completar. Es **obligatorio** completar únicamente las secciones marcadas (`##### EDITAR ESTA ZONA` / `TODO`), sin agregar contenido adicional.

La función `search_algorithm` debe devolver el nodo con la solución encontrada (o `None` si no se encontró una), junto con un diccionario de métricas que incluya como mínimo:

- `solution_found`: `True` si se encontró la solución, `False` en caso contrario.
- `nodes_explored`: cantidad de nodos explorados.
- `states_visited`: cantidad de estados distintos visitados.
- `nodes_in_frontier`: cantidad de nodos que quedaron en la frontera al finalizar.
- `max_depth`: máxima profundidad explorada.
- `cost_total`: costo total para encontrar la solución.

## Código de apoyo

Este ejercicio trae su propia copia de [`aima_libs/`](aima_libs/) (igual a la de [`../aima_libs/`](../aima_libs/)) para que la carpeta se pueda resolver y entregar de forma autocontenida.

## Cómo abrirla

Con el entorno del repositorio ya configurado (ver [Quick start](../../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir la notebook. Podés usar como referencia [`../02_algoritmos_de_busqueda.ipynb`](../02_algoritmos_de_busqueda.ipynb), donde se implementa búsqueda primero en anchura.
