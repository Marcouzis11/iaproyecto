# Clasificación de hallazgos en radiografías de tórax

Proyecto académico de Inteligencia Artificial. Se propone comenzar con la clasificación binaria de un hallazgo y evaluar una ampliación multietiqueta según los datos y resultados.

**Estado:** flujo de preparación implementado y comprobado con datos sintéticos. Hay auditoría, split por paciente y exportación de arrays para entrenamiento, validación y test. Todavía no se descargó ni procesó un dataset real, ni se entrenó un modelo.

## Demo

La prueba del pipeline se ejecuta con `configs/demo.json`; genera y prepara imágenes artificiales, no radiografías. La demo del modelo y la presentación en GitHub Pages siguen pendientes.

## Sobre el proyecto

El objetivo es estimar etiquetas de un dataset de radiografías de tórax y medir la generalización sobre pacientes reservados. Es un prototipo académico. El alcance y las decisiones previstas se describen en [el plan de trabajo](PLAN_PROYECTO_RX_TORAX.md).

### Contexto académico

Inteligencia Artificial, Ingeniería en Informática, Facultad de Ingeniería, Centro Regional Universitario Córdoba - IUA, Universidad de la Defensa Nacional. Docente: Ing. Hernando Alexis González. Año: 2026, según la consigna local. Modalidad e integrantes pendientes de documentar.

### Construido con

El preparador usa Python 3.11–3.13, NumPy 2.3.5 y Pillow 12.3.0. Las dependencias están fijadas en `pyproject.toml`. Las librerías de modelado se incorporarán cuando se implemente el entrenamiento.

## El dataset

Fuentes candidatas conservadas en `datasets/`: [NIH ChestX-ray](https://nihcc.app.box.com/v/ChestXray-NIHCC) y [CheXpert](https://stanfordmlgroup.github.io/competitions/chexpert/). La selección, el volumen, las etiquetas y las condiciones de uso quedan pendientes de verificar. Descargar los datos en `data/raw/`; no versionar las imágenes ni los metadatos de pacientes.

## Metodología

Está implementada la lectura de CSV genérico, CheXpert y NIH; la auditoría de archivos y etiquetas; la detección de duplicados exactos; la separación por paciente; y el redimensionado y escalado reproducibles. El EDA sobre datos reales, baseline, comparación de clasificadores y evaluación final siguen pendientes. Ver [guía de preparación](docs/PREPARAR_DATOS.md).

## Resultados

Pendientes de entrenar y evaluar. No hay métricas medidas.

## Estructura del proyecto

```text
.
├── readme.md
├── pyproject.toml
├── configs/
├── scripts/
├── examples/
├── consigna.pdf
├── PLAN_PROYECTO_RX_TORAX.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── rx_torax/          # Paquete ejecutable; data/ y preprocessing/
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

Con Python 3.12 instalado, desde la raíz del repositorio:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

En este PC ya existe el entorno instalado. No es necesario activarlo para usar los comandos siguientes.

## Uso

Descargar imágenes y metadatos, editar el JSON correspondiente en `configs/` y ejecutar, por ejemplo:

```powershell
.\.venv\Scripts\python.exe -m rx_torax.prepare --config configs/chexpert.json
```

La [guía de preparación](docs/PREPARAR_DATOS.md) explica las rutas esperadas, los tres formatos, las particiones oficiales, la demo sintética y cómo cargar `X_train`, `X_val`, `X_test` y sus etiquetas. Los comandos de entrenamiento y predicción del modelo se incorporarán después.

Para comprobar el código:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Roadmap

- Definir la propuesta formal, el dataset y el hallazgo inicial.
- Ejecutar el preparador sobre una muestra real y completar el EDA y la revisión visual.
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
