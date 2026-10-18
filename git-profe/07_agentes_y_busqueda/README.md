# Clase 7 - Agentes y resolución de problemas mediante búsqueda

Se introduce el concepto de **agente racional** y se aborda la resolución de problemas mediante algoritmos de búsqueda, usando como caso de estudio la **Torre de Hanoi**: primero se modela el problema (estados, acciones, costo), después se construye el árbol de búsqueda y se aplica búsqueda primero en anchura, y por último se visualiza la solución encontrada con un simulador.

Algoritmos que se ven en la teoría:

- **Búsqueda no informada:** primero en anchura (BFS), costo uniforme (Dijkstra), primero en profundidad (DFS), profundidad limitada y profundidad limitada con profundidad iterativa.
- **Búsqueda informada:** voraz (*greedy*) primero el mejor, y A*.

## Teoría

- [`teoria/README.md`](teoria/README.md) — resumen teórico: agentes racionales, programas de agentes, resolución de problemas mediante búsqueda y algoritmos de búsqueda informada y no informada.
- [`heuristicas_torre_de_hanoi.md`](heuristicas_torre_de_hanoi.md) — cómo definir una función heurística para la Torre de Hanoi (necesaria para experimentar con búsqueda informada).

## Notebooks

- [`01_torre_de_hanoi_implementacion.ipynb`](01_torre_de_hanoi_implementacion.ipynb) — definición del problema: espacio de estados, estado inicial y objetivo, y las clases `StatesHanoi`, `ActionHanoi` y `ProblemHanoi`.
- [`02_algoritmos_de_busqueda.ipynb`](02_algoritmos_de_busqueda.ipynb) — árbol de búsqueda, colas (FIFO, LIFO y de prioridad), implementación de búsqueda primero en anchura y medición de su rendimiento (tiempo y memoria).
- [`03_simulador_torre_de_hanoi.ipynb`](03_simulador_torre_de_hanoi.ipynb) — (opcional) cómo usar el simulador hecho con PyGame para ver al agente ejecutando la solución que encontró.

## Ejercicio

- [`ejercicios/`](ejercicios/) — evaluación práctica: implementar un algoritmo de búsqueda distinto a BFS para resolver la Torre de Hanoi. Ver su [README](ejercicios/README.md) para la consigna y la rúbrica de evaluación.

## Código de apoyo

- [`aima_libs/`](aima_libs/) — implementación del problema y del árbol de búsqueda, basada en el código del libro *Artificial Intelligence: A Modern Approach* (Russell y Norvig, [aima-python](https://github.com/aimacode/aima-python)). Las notebooks lo importan directamente. Ver su [README](aima_libs/README.md) para el detalle de cada clase.
- [`simulator/`](simulator/) — simulador visual con PyGame. Ver su [README](simulator/README.md) para el formato de los archivos `initial_state.json` y `sequence.json`.
- [`img/`](img/) — imágenes usadas por las notebooks y por el documento de heurísticas.
- [`referencias/`](referencias/) — artículo citado en [`heuristicas_torre_de_hanoi.md`](heuristicas_torre_de_hanoi.md) (Garcia & Chávez R., sobre una heurística más sofisticada para la Torre de Hanoi), guardado localmente porque el link original ya no funciona.

## Notas

- Al ejecutar `03_simulador_torre_de_hanoi.ipynb` se generan `initial_state.json` y `sequence.json` en esta carpeta (no se versionan). Para ver la animación, movelos a [`simulator/`](simulator/) y ejecutá desde ahí `python simulation_hanoi.py` (en Linux/Mac, `python3`). Ojo: `simulator/` ya trae un par de archivos de ejemplo, que se pisan al moverlos.
- En `02_algoritmos_de_busqueda.ipynb`, la celda que prueba búsqueda en anchura con 4 discos **tarda muchísimo a propósito**: no controla los estados ya explorados y entra en bucles largos. Es parte de la explicación — se puede interrumpir la ejecución, y la celda siguiente muestra la versión que soluciona el problema.

## Fuentes de datos

No hay datasets: el problema se define por código (`aima_libs/`). Solo se necesita `pygame` (ya incluido en las dependencias del repositorio) para el simulador.

## Cómo abrirlas

Con el entorno del repositorio ya configurado (ver [Quick start](../README.md#quick-start)):

```bash
jupyter notebook
```

y elegí el kernel **"Python (IA)"** al abrir cada notebook.
