# Clasificación de hallazgos en radiografías de tórax

Proyecto académico de Inteligencia Artificial. Se propone comenzar con la clasificación binaria de un hallazgo y evaluar una ampliación multietiqueta según los datos y resultados.

**Estado:** planificación y estructura inicial. No hay datos descargados, código de entrenamiento, modelo evaluado ni demo funcional.

## Demo

Pendiente de implementar y publicar. `docs/` queda preparado para la presentación estática de GitHub Pages.

## Sobre el proyecto

El objetivo es estimar etiquetas de un dataset de radiografías de tórax y medir la generalización sobre pacientes reservados. Es un prototipo académico. El alcance y las decisiones previstas se describen en [el plan de trabajo](PLAN_PROYECTO_RX_TORAX.md).

### Contexto académico

Inteligencia Artificial, Ingeniería en Informática, Facultad de Ingeniería, Centro Regional Universitario Córdoba - IUA, Universidad de la Defensa Nacional. Docente: Ing. Hernando Alexis González. Año: 2026, según la consigna local. Modalidad e integrantes pendientes de documentar.

### Construido con

Todavía no hay implementación ni dependencias declaradas. El plan propone Python, NumPy, pandas, OpenCV, visualización y scikit-learn; las versiones se fijarán al implementar el entorno.

## El dataset

Fuentes candidatas conservadas en `datasets/`: [NIH ChestX-ray](https://nihcc.app.box.com/v/ChestXray-NIHCC) y [CheXpert](https://stanfordmlgroup.github.io/competitions/chexpert/). La selección, el volumen, las etiquetas y las condiciones de uso quedan pendientes de verificar. Descargar los datos en `data/raw/`; no versionar las imágenes ni los metadatos de pacientes.

## Metodología

El plan contempla auditoría y particiones por paciente, EDA, preparación de imágenes, baseline, comparación de clasificadores y evaluación final. Es una propuesta de trabajo; aún no se ejecutaron experimentos.

## Resultados

Pendientes de entrenar y evaluar. No hay métricas medidas.

## Estructura del proyecto

```text
.
├── readme.md
├── consigna.pdf
├── PLAN_PROYECTO_RX_TORAX.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── data/
│   ├── preprocessing/
│   ├── training/
│   ├── evaluation/
│   └── inference/
├── models/
├── tests/
├── docs/
│   ├── ORGANIZACION.md
│   ├── img/
│   └── assets/
├── datasets/
├── Slides/
└── git-profe/
```

Ver [organización y ramas](docs/ORGANIZACION.md) para la responsabilidad de cada directorio y el flujo de integración. `data/` y `models/` conservan solo marcadores en Git; los datos y artefactos quedan locales.

## Instalación

Aún no hay entorno instalable. Falta crear el manifiesto de dependencias con versiones exactas y documentar el entorno virtual, conforme a la consigna. No hay comandos de instalación validados para el proyecto.

## Uso

Por ahora, consultar el plan y la documentación de organización. Los comandos de carga, entrenamiento, evaluación y predicción se documentarán cuando estén implementados.

## Roadmap

- Definir la propuesta formal, el dataset y el hallazgo inicial.
- Implementar datos, EDA y preprocesamiento reproducible.
- Entrenar, evaluar y guardar el modelo con su predictor.
- Completar el informe y publicar la presentación.

## Autores

Integrantes y enlaces personales pendientes de documentar.

## Licencia

El proyecto todavía no declara una licencia propia. Las fuentes de datos y el material del docente tienen sus condiciones de uso; no se les asigna automáticamente una licencia del proyecto.

## Agradecimientos y referencias

- [Lineamientos del proyecto final](consigna.pdf).
- [Consigna y plantilla del docente](git-profe/trabajo_final/README.md).
- Material de clase en `Slides/` y `git-profe/`.
- Fuentes de datos citadas en la sección «El dataset».
