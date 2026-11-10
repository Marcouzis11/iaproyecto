# Notebooks del flujo de preparación

1. **`01_preparacion_radiografias.ipynb`**: configuración, implementación completa, lectura, auditoría, split por paciente, EDA visual de train, exportación y carga de los arrays finales.
2. **`02_pruebas_pipeline.ipynb`**: 12 pruebas sobre las funciones contenidas en el primer notebook. Carga solamente las celdas de definiciones, no ejecuta su flujo ni accede a los datos reales.

El primer notebook contiene todas las funciones: no importa módulos locales `.py`, no requiere JSON de `configs/` y permite trabajar desde sus propias celdas. Los scripts Python anteriores se conservan como alternativa de consola. Si se modifica una implementación, mantener ambas versiones coherentes y volver a ejecutar las pruebas de notebooks y de scripts.

## Abrir los notebooks

Con el entorno del proyecto creado (ver «Instalación» en el [README](../README.md)) y activado, desde la raíz del repositorio:

```bash
python -m pip install -e ".[notebooks]"
python -m ipykernel install --prefix .venv --name iaproyecto --display-name "Python (iaproyecto)"
python -m notebook notebooks/01_preparacion_radiografias.ipynb
```

Elegir el kernel **Python (iaproyecto)** y **Run All / Ejecutar todo**.

Los notebooks cubren la preparación de los datos. El entrenamiento, la evaluación y la predicción se corren con los comandos `rx-*`; `scripts/flujo_completo.sh demo` muestra el flujo entero sin descargar el dataset.

## Usar radiografías reales

El modo inicial es `DATASET = 'demo'`: procesa 120 imágenes artificiales y permite ejecutar todo sin descargar un dataset. No son radiografías.

En la sección 1 elegir `generic`, `chexpert` o `nih` y ajustar `metadata`, `image_root` y `target` dentro de `opciones`. Los datos deben estar descargados. La guía `docs/PREPARAR_DATOS.md` explica los formatos y las particiones oficiales.

El notebook detecta la raíz del clon al abrir desde el repositorio o desde `notebooks/`. Si se copia a otro sitio, ajustar `PROJECT_ROOT` al directorio deseado. Todas las rutas de datos se interpretan desde esa raíz.

Cada ejecución completa crea `data/processed/<dataset>_notebook_<identificador>/`, con `X_train.npy`, `y_train.npy`, sus equivalentes de validación/test, los CSV y los informes. Al terminar quedan además las variables `X_train`, `y_train`, `X_val`, `y_val`, `X_test`, `y_test` disponibles en el kernel.

Para repetir una exportación, reiniciar y ejecutar todo: se crea otra salida. No volver a ejecutar solo la celda de exportación sobre una salida existente. Los notebooks versionados se guardan sin salidas; la comprobación realizada usó una ejecución completa con kernel nuevo y pasó también las 12 pruebas.
