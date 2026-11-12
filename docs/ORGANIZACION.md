# Organización del repositorio y flujo de trabajo

## Requisitos de la consigna

- **Separación de capas** (sección 2.1): datos en `data/` fuera de git, notebooks en `notebooks/`, código modular en `src/` y artefactos en `models/`.
- **Control de versiones** (secciones 2.1 y 5): ramas para el desarrollo y commits que reflejen incrementos lógicos.
- **Reproducibilidad** (sección 2.3): entorno virtual, dependencias con versiones fijas en `pyproject.toml` y `requirements.txt`, y semilla 42 en todo proceso aleatorio.
- **Plantilla del docente:** `README.md`, `LICENSE`, `tests/` y la página estática en `docs/`.

## Directorios

| Ruta | Contenido |
|---|---|
| `data/raw/` | NIH descargado, sin modificar. Fuera de git. |
| `data/processed/` | Una carpeta por preparación: arrays `X`/`y`, CSV por conjunto, exclusiones y reportes. Fuera de git. |
| `src/rx_torax/data/` | Lectura de metadatos (NIH, CheXpert, CSV genérico), auditoría y split por paciente. |
| `src/rx_torax/preprocessing/` | Lectura de imágenes y transformación a 224×224. La usan la preparación y la predicción. |
| `src/rx_torax/training/` | DenseNet121, aumento de datos y entrenamiento. Nunca abre test. |
| `src/rx_torax/evaluation/` | Métricas, bootstrap por paciente, evaluación única en test y comparación pareada. |
| `src/rx_torax/inference/` | `rx-predecir`: carga `modelo.pt` y predice sobre archivos de imagen. |
| `configs/` | JSON de preparación (`nih*.json`, `demo.json`) y de entrenamiento (`modelo_*.json`). |
| `models/` | Un directorio por modelo. En git solo está el modelo final (B); el resto se regenera. |
| `notebooks/` | Análisis exploratorio de NIH (guardado con resultados), preparación en celdas y sus pruebas. |
| `tests/` | Pruebas automáticas con datos sintéticos (`unittest`). |
| `scripts/` | `flujo_completo.sh` (demo o NIH de punta a punta) y `preparar.ps1` (Windows). |
| `examples/` | Cuatro radiografías del test oficial y un ejemplo de carga de arrays. |
| `docs/` | Página de GitHub Pages (`index.html`), informe en PDF, figuras y documentación de cada etapa. |

Cada capa depende solo de las anteriores: la preparación no sabe nada del modelo, el entrenamiento recibe arrays ya preparados y la inferencia reutiliza la misma transformación que la preparación.

## Ramas

| Rama | Contenido |
|---|---|
| `main` | Versión entregable. La cátedra evalúa esta rama. |
| `feature/preprocesamiento` | Auditoría, split por paciente, selección 40/60 y preparación de NIH. |
| `feature/modelado` | Entrenamiento, evaluación, predicción, modelos A, B y C, y documentación de la entrega. Parte de `feature/preprocesamiento`. |

Cada etapa se desarrolla en su rama y se integra en `main` con un pull request cuando está revisada.

## Commits

Mensajes en español con prefijo semántico: `feat:` para funcionalidad nueva, `docs:` para documentación y resultados, `chore:` para organización. Cada commit deja el código funcionando y las pruebas pasando.

## Experimentos

Cada preparación, entrenamiento y evaluación guarda un `report.json` con la configuración completa, la semilla, las versiones de las librerías y las métricas. Ninguna salida se sobrescribe: los comandos se niegan a escribir en una carpeta existente, y `rx-evaluar` no evalúa dos veces el mismo conjunto.
