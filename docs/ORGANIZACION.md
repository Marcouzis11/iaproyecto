# Organización y flujo de trabajo

## Requisitos aplicados

- `consigna.pdf`, sección 2.1 (p. 3): separar datos, notebooks, código modular y modelos; trabajar con ramas.
- `consigna.pdf`, sección 5 (pp. 10–11): commits lógicos y separación de responsabilidades.
- `git-profe/trabajo_final/README.md`, apartado «Estructura de la plantilla»: sumar `tests/`, `docs/img/` y `docs/assets/`.
- Los subdirectorios de `src/` y los nombres de ramas son decisiones de organización de este proyecto, no nombres impuestos por la cátedra.

## Directorios

| Ruta | Contenido esperado |
|---|---|
| `data/raw/` | Imágenes y metadatos originales, sin modificar. |
| `data/processed/` | Datos limpios, representaciones y particiones por paciente. |
| `notebooks/` | Exploración y experimentos; reutilizar los módulos de `src/`. |
| `src/data/` | Lectura, auditoría y partición de los datos. |
| `src/preprocessing/` | Transformaciones y construcción de entradas. |
| `src/training/` | Baseline, ajuste de modelos y configuración de experimentos. |
| `src/evaluation/` | Métricas, comparación de modelos y análisis de errores. |
| `src/inference/` | Carga del artefacto y predicción sobre imágenes nuevas. |
| `models/` | Modelos entrenados y artefactos asociados. |
| `tests/` | Comprobaciones del pipeline cuando haya implementación. |
| `docs/` | Informe, decisiones y futura presentación estática. |
| `docs/img/` | Capturas y gráficos reales para el README y la presentación. |
| `docs/assets/` | Estilos y recursos de la presentación. |
| `datasets/` | Enlaces a las fuentes originales; se conserva su ubicación. |
| `Slides/`, `git-profe/` | Material de referencia existente, conservado. |

Git no guarda carpetas vacías: los archivos `.gitkeep` permiten conservar la estructura al clonar. El contenido de `data/` y `models/` está ignorado, salvo esos marcadores. Los enlaces de `datasets/` se mantienen versionados; los archivos descargados van en `data/raw/`.

## Ramas locales

| Rama | Uso |
|---|---|
| `main` | Versiones estables y entregables revisados. |
| `develop` | Integración del trabajo antes de pasar a `main`. |
| `chore/estructura-proyecto` | Preparación inicial de directorios y documentación. |
| `feature/datos-eda` | Selección del dataset, auditoría y exploración. |
| `feature/preprocesamiento` | Limpieza, particiones y transformaciones reproducibles. |
| `feature/modelado` | Baseline, entrenamiento y comparación de configuraciones. |
| `feature/evaluacion-inferencia` | Evaluación final, persistencia y predictor. |
| `docs/informe-demo` | README final, informe y página estática de presentación. |

Las ramas de trabajo parten de la estructura inicial. Antes de comenzar una etapa, incorporar el estado actualizado de `develop`:

```bash
git switch feature/datos-eda
git merge develop
```

Guardar avances pequeños con mensajes como `feat: agregar auditoría de etiquetas`. Integrar la rama terminada en `develop`, resolver conflictos y verificar el flujo afectado. Pasar a `main` cuando la entrega correspondiente esté revisada. Eliminar las ramas terminadas cuando ya no se necesiten y crear nuevas desde `develop` para trabajos posteriores. No desarrollar simultáneamente el mismo cambio en varias ramas.

Estas ramas se crean localmente. Su publicación y la configuración de GitHub Pages quedan para una etapa posterior. Para Pages, la plantilla propone `main` y `/docs`; todavía no hay una demo publicada.

## Pendientes de implementación y entrega

La estructura es un punto de partida, no una entrega funcional. Quedan el Project Charter, la elección definitiva del dataset y del hallazgo, el entorno virtual y `pyproject.toml` con versiones exactas, la semilla global, los notebooks/scripts, el modelo, las métricas y la demo. El README debe completarse siguiendo la plantilla con datos reales del equipo y resultados medidos. El plan conceptual está en `PLAN_PROYECTO_RX_TORAX.md`; esta organización incorpora los requisitos de entrega que ese plan dejó expresamente fuera de su fundamento.
