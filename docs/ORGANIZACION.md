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
| `models/` | Un directorio por modelo. En git están el modelo final (B) completo y los reportes livianos de todos los modelos y comparaciones (`report.json`, `historial.csv`); los pesos de A, C y el control se regeneran. |
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
| `chore/entrega-mvp-final` | Integración continua, verificación de la instalación en Windows y material de la presentación del MVP. |

Cada etapa se desarrolla en su rama y se integra en `main` con un pull request. `feature/modelado` salió de `feature/preprocesamiento` y las dos entraron juntas en el PR #1; la documentación posterior entró por ramas `docs/*` (PR #2 y #3). Los PR se integraron sin revisión formal en GitHub.

## Commits

Mensajes en español con prefijo semántico: `feat:` para funcionalidad nueva, `docs:` para documentación y resultados, `chore:` para organización y `ci:` para la integración continua. Cada commit deja el código funcionando y las pruebas pasando.

El título dice qué cambia y el cuerpo, qué problema resuelve. Por ejemplo:

```text
ci: correr las pruebas y rx-predecir en cada push

La instalación solo se había verificado en macOS; ahora se prueba en Ubuntu y Windows.
```

## Integración continua

`.github/workflows/tests.yml` corre en cada push y pull request, en Ubuntu (Python 3.11) y Windows (Python 3.13): instala el proyecto con las versiones fijadas, ejecuta las pruebas de `tests/` y prueba `rx-predecir` con las radiografías de ejemplo. Un pull request a `main` se integra con la ejecución en verde.

## Experimentos

Cada preparación, entrenamiento y evaluación guarda un `report.json` con la configuración, la semilla, las versiones de las librerías y las métricas, y esos reportes están en git. La preparación, el entrenamiento y la evaluación se niegan a escribir en una carpeta existente, y `rx-evaluar` no evalúa dos veces el mismo conjunto.
