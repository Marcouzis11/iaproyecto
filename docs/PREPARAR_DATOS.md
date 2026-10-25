# Preparar radiografías para entrenamiento, validación y test

El flujo está implementado. Se verificó con imágenes sintéticas y CSV de prueba de los tres formatos; todavía no se ejecutó contra una descarga real de NIH o CheXpert. No incluye entrenamiento ni descarga automática. Descargar los datos de las fuentes de `datasets/` y descomprimirlos antes de preparar.

## 1. Entorno

Abrir PowerShell en el repositorio:

```powershell
cd C:\Users\marco\OneDrive\Documentos\GitHub\iaproyecto
```

En este PC ya se dejó instalado `.venv`. Para recrearlo en otro equipo, instalar Python 3.12 y ejecutar:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

No es necesario activar el entorno. `pyproject.toml` fija las versiones de NumPy y Pillow; Python admitido: 3.11–3.13. El recorrido se comprobó con Python 3.12.14. Pillow se usa para la lectura y el redimensionado de imágenes, en lugar de agregar OpenCV como dependencia de esta primera etapa.

## 2. Elegir el formato de entrada

Las rutas de los JSON son relativas al directorio desde el que se ejecuta el comando. Ejecutar desde la raíz del repositorio. Los nombres de hallazgos en los ejemplos son configurables: no son una elección definitiva del proyecto.

### CheXpert

Editar `configs/chexpert.json`. El ejemplo espera:

```text
data/raw/CheXpert-v1.0-small/
├── train.csv
└── train/
    └── patient00001/study1/view1_frontal.jpg
```

`image_root` debe ser el directorio al que se agrega literalmente el valor de `Path` del CSV. Si `Path` comienza por `CheXpert-v1.0-small/train/...`, usar `data/raw`. Si empieza por `train/...`, usar `data/raw/CheXpert-v1.0-small`. No se adivinan ni corrigen rutas silenciosamente.

El adaptador requiere `Path` y una columna de hallazgo como `Pleural Effusion`. Extrae el identificador `patientNNNNN` de la ruta. Si `frontal_only` es `true`, requiere `Frontal/Lateral` y conserva `Frontal`. Solo acepta etiquetas explícitas 0 y 1; excluye y registra -1, vacío y valores inválidos. Esta política reduce la muestra y debe documentarse en el informe.

```powershell
.\.venv\Scripts\python.exe -m rx_torax.prepare --config configs/chexpert.json
```

El JSON de ejemplo subdivide únicamente `train.csv` en un train/val/test interno. **No es una evaluación sobre el test oficial de CheXpert.** Los archivos oficiales no suministrados se conservan fuera del flujo. Si se cuenta con particiones oficiales utilizables, preparar un CSV con columna `split`, como se explica más abajo, para conservarlas; no renombrar automáticamente el `valid.csv` oficial como test.

### NIH ChestX-ray14

Editar `configs/nih.json`. Ubicar `Data_Entry_2017.csv` e imágenes descomprimidas debajo de `data/raw/nih`. Se buscan imágenes recursivamente por `Image Index`, por lo que pueden conservarse los directorios `images_001/images/`, etc. Nombres ambiguos en distintas carpetas se excluyen y registran.

Se requieren `Image Index`, `Patient ID`, `Finding Labels` y, con filtro frontal, `View Position`. `target: "Effusion"` significa 1 si ese hallazgo aparece en las etiquetas separadas por `|`, y 0 si no aparece. Es ausencia de anotación positiva para ese hallazgo; no garantiza ausencia clínica ni que la imagen sea normal. Los casos con otros hallazgos se conservan como negativos para el target si no incluyen el hallazgo elegido.

Si están disponibles `train_val_list.txt` y `test_list.txt`, colocarlos junto a `Data_Entry_2017.csv`. Se detectan automáticamente: se conserva el test listado y se obtiene validación solo del grupo train/val. Si aparece una sola lista o un paciente cruza train/test, el programa se detiene. Con una descarga parcial, el test resultante contiene únicamente las imágenes disponibles y válidas de la lista; el reporte permite documentar esa limitación. Sin listas ni columna `split`, se genera una partición interna.

```powershell
.\.venv\Scripts\python.exe -m rx_torax.prepare --config configs/nih.json
```

### Radiografías propias o un CSV normalizado

Editar `configs/generic.json`. Colocar las imágenes en `data/raw/mis_radiografias/images/` y crear `metadata.csv`:

```csv
image_path,patient_id,target,view
images/rx_001.png,paciente_001,1,PA
images/rx_002.png,paciente_002,0,AP
images/rx_003.png,paciente_001,1,PA
```

Estos tres registros solo ilustran el formato: no alcanzan para preparar tres conjuntos. Para una partición interna se requieren al menos seis pacientes, con soporte suficiente para tener positivos y negativos en cada conjunto. Un CSV grande también puede fallar si los positivos pertenecen a muy pocos pacientes.

`image_path` debe estar dentro de `image_root`; se admite una ruta absoluta solo si sigue dentro de esa carpeta. `patient_id` es obligatorio y debe identificar a la misma persona de forma consistente. `view` es opcional salvo que se active `frontal_only`; en ese caso se admiten `PA`, `AP` o `FRONTAL`. No usar el nombre de archivo como sustituto del paciente si una persona tiene varias imágenes. No unir fuentes con identificadores incompatibles sin armonizarlos previamente.

```powershell
.\.venv\Scripts\python.exe -m rx_torax.prepare --config configs/generic.json
```

También se puede ejecutar `scripts/preparar.ps1 -Config configs/generic.json` si la política local permite scripts PowerShell.

### Conservar particiones explícitas

Los tres adaptadores admiten una columna `split` completa con `train`, `val` (o `valid`) y `test`. No se reasignan esas filas. Si solo hay `train` y `test`, se conserva test y se separa validación por paciente dentro de train. En ese caso, la proporción de validación interna es `ratios[1] / (ratios[0] + ratios[1])`; el tamaño del test oficial no se modifica.

No se admiten asignaciones parciales, clases ausentes tras la auditoría ni pacientes compartidos entre conjuntos. En NIH, elegir las listas oficiales o la columna `split`; no usar ambas.

## 3. Qué hace el comando

1. Valida configuración y columnas. Revisa etiquetas, pacientes y vistas.
2. Abre las imágenes y registra dimensiones, modo y profundidad. Excluye archivos ausentes, ilegibles y formatos no admitidos.
3. Detecta duplicados por hash de píxeles originales en grises. Conserva una copia si coincide paciente, etiqueta y split; excluye todas las copias si hay conflictos entre etiquetas, pacientes o particiones. No detecta automáticamente todas las variantes casi idénticas o recomprimidas.
4. Conserva particiones explícitas o busca un reparto por paciente con semilla fija. Intenta aproximar las proporciones de imágenes y clases sin dividir pacientes. La proporción exacta puede variar por el tamaño de cada grupo; revisar `report.json`.
5. Convierte a grises y escala de forma fija: uint8/255 o uint16/65535. Redimensiona conservando proporción, sin recortar, y agrega bordes negros hasta `image_size × image_size`. Por defecto usa 224; validar visualmente si esa resolución conserva detalle suficiente para el hallazgo.
6. Calcula media y desviación únicamente de train, después del redimensionado y padding. Con `normalization: "unit"` conserva [0,1]; con `"zscore"` aplica a los tres conjuntos la media y desviación de train. Los valores de z-score pueden quedar fuera de [0,1].
7. Exporta arrays, manifiestos y reporte. Comprueba que todos los registros de entrada estén contabilizados como aceptados o excluidos.

No se imputa el target, no se balancea test ni validación, no se generan imágenes sintéticas de pacientes y no se eliminan imágenes por ser casos raros. No se aplica SMOTE, filtros o augmentation automáticamente. Si se prueba balanceo más adelante, hacerlo solo durante el entrenamiento.

Se admiten PNG/JPEG y TIFF de un solo frame, en grises de 8/16 bits o RGB de 8 bits. Se rechazan otros modos para evitar conversiones silenciosas. **DICOM no está implementado**: requiere una etapa específica que respete su interpretación de intensidades. Los originales nunca se sobrescriben.

## 4. Archivos listos para entrenar y testear

En `output` se generan:

```text
X_train.npy       y_train.npy       train.csv
X_val.npy         y_val.npy         val.csv
X_test.npy        y_test.npy        test.csv
exclusiones.csv
report.json
preprocessing.json
config.json
labels.json
```

`X` tiene forma `(N, H, W)` y dtype `float32`. `y` tiene forma `(N,)`, dtype `int64` y clases 0/1. Cada fila de los CSV corresponde a la posición `array_index` del array e incluye paciente, ruta original y hash. El orden de las etiquetas coincide con el de las imágenes.

Para cargarlos sin leer todo el archivo en RAM:

```python
from pathlib import Path
import numpy as np

carpeta = Path("data/processed/mis_radiografias_v1")
X_train = np.load(carpeta / "X_train.npy", mmap_mode="r", allow_pickle=False)
y_train = np.load(carpeta / "y_train.npy", allow_pickle=False)
X_val = np.load(carpeta / "X_val.npy", mmap_mode="r", allow_pickle=False)
y_val = np.load(carpeta / "y_val.npy", allow_pickle=False)
X_test = np.load(carpeta / "X_test.npy", mmap_mode="r", allow_pickle=False)
y_test = np.load(carpeta / "y_test.npy", allow_pickle=False)

# Vista para un clasificador tabular como KNN:
X_train_vectores = X_train.reshape(len(X_train), -1)
X_val_vectores = X_val.reshape(len(X_val), -1)
X_test_vectores = X_test.reshape(len(X_test), -1)
```

Entrenar solo con train; seleccionar configuraciones con val; evaluar el modelo final con test. Los CSV incluyen metadatos para trazabilidad: no introducir automáticamente `patient_id`, rutas o hashes como features.

```powershell
.\.venv\Scripts\python.exe examples/cargar_datos.py --data data/processed/mis_radiografias_v1
```

El uso de memmap reduce la RAM necesaria para preparar/cargar arrays, pero un clasificador posterior puede copiarlos en memoria. A 224×224 float32, cada imagen preparada ocupa aproximadamente 196 KiB; 100.000 imágenes requieren unos 18,7 GiB solo para `X`. Se comprueba espacio libre antes de exportar. Para empezar, usar una muestra de pacientes con suficiente soporte por clase y registrar que la descarga es parcial.

El programa no sobrescribe salidas existentes: cambiar `output` a una carpeta nueva para otro experimento. La salida final aparece solo si termina el flujo; ante un fallo no se deja una carpeta final incompleta. Si no puede formar particiones válidas, guarda las exclusiones en `<output>.audit.csv` cuando esa ruta no existe previamente.

## 5. Prueba inmediata sin descargar radiografías

En este PC ya se ejecutaron estos comandos. La demo quedó en `data/processed/demo_sintetica_v1`. Para cargarla:

```powershell
.\.venv\Scripts\python.exe examples/cargar_datos.py --data data/processed/demo_sintetica_v1
```

Para repetir desde cero en otro clon:

```powershell
.\.venv\Scripts\python.exe -m rx_torax.demo
.\.venv\Scripts\python.exe -m rx_torax.prepare --config configs/demo.json
```

Genera 120 imágenes artificiales de 60 pacientes ficticios, con 84/18/18 imágenes en train/val/test. **No son radiografías ni permiten medir rendimiento clínico.** Es una comprobación de instalación, lectura, particiones y exportación. Si las carpetas de demo ya existen, no repetir los comandos de generación: usar los archivos existentes o cambiar las rutas de entrada/salida en una copia del JSON.

Pruebas automatizadas:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 6. Antes de entrenar sobre datos reales

Revisar `exclusiones.csv`, los conteos de `report.json` y una muestra visual de imágenes preparadas. Confirmar el target, el esquema de etiquetas, la independencia por paciente y la idoneidad de la resolución. Las comprobaciones automáticas no garantizan calidad clínica ni corrección del etiquetado. La política de usar solo 0/1 explícitos en CheXpert y las exclusiones pueden introducir sesgos de selección que deben informarse.

## Referencias de implementación

- Plan local: `PLAN_PROYECTO_RX_TORAX.md`, etapas 1–4.
- Ejemplos del docente: split/stratify, normalización, desbalance y EDA de imágenes en `git-profe/`.
- [CheXpert: descripción oficial y etiquetas inciertas](https://stanfordmlgroup.github.io/competitions/chexpert/).
- [Pillow: transformaciones de imágenes](https://pillow.readthedocs.io/en/stable/reference/ImageOps.html).
- La búsqueda de particiones por paciente y los adaptadores son implementación propia del proyecto; no se atribuyen a una receta literal de los slides.
