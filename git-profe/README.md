# Inteligencia Artificial

> Material de la asignatura **Inteligencia Artificial**.

## Sobre este repositorio

Acá se publica el material práctico de la cursada: ejercicios, ejemplos de código y recursos en Python. El contenido se organiza en carpetas numeradas (`00_...`, `01_...`, etc.), una por unidad temática, y se va publicando de forma incremental a medida que avanza la cursada.

## Contenido publicado

- [Clase 1 - Introducción a Python](01_introduccion_python/)
- [Clase 2 - Introducción al análisis de datos](02_introduccion_analisis_datos/)
- [Clase 3 - Análisis exploratorio de datos (EDA)](03_analisis_exploratorio_datos_eda/)
- [Clase 4 - Medidas de asociación, datos faltantes y outliers](04_asociacion_faltantes_outliers/)
- [Clase 5 - Procesamiento y limpieza de datos](05_procesamiento_y_limpieza_de_datos/)
- [Clase 6 - Feature engineering y EDA avanzado](06_feature_engineering_avanzado/)
- [Clase 7 - Agentes y resolución de problemas mediante búsqueda](07_agentes_y_busqueda/)
- [Clase 8 - Optimización: búsqueda local y espacios continuos](08_optimizacion/)
- [Clase 9 - Aprendizaje automático](09_aprendizaje_automatico/)
- [Clase 10 - Regresión](10_regresion/)

## Material complementario

- [`material_complementario/`](material_complementario/) — notebooks y ejercicios de repaso de Python, NumPy, Pandas, Matplotlib y Seaborn. No es parte del temario de la materia ni sigue la numeración de clases.

## Extra

- [`extra/`](extra/) — material adicional fuera del temario de la materia: por ahora, una introducción a OpenCV (ver [`extra/computer_vision/`](extra/computer_vision/)).

## Trabajo final

- [`trabajo_final/`](trabajo_final/) — consigna y plantilla obligatoria (estructura de carpetas + `README.md` + demo en GitHub Pages) para el repositorio del trabajo final.

## Organización del repositorio (branches y tags)

- Todo el material vive en la rama `master`. No hay otras ramas de desarrollo: alumnos y docentes trabajan sobre `master`.
- Durante la cursada, el contenido se actualiza sobre `master` a medida que se dictan las clases. Para tener siempre el material al día, hace `git pull` periódicamente.
- Al finalizar cada cohorte se crea un **tag** (por ejemplo `2025`, `2026`) que congela el estado del repositorio para esa cursada. Así, aunque el contenido de `master` siga evolucionando en años siguientes, cada cohorte conserva una referencia fija a lo que efectivamente se dictó en su año.
- Si sos de una cohorte anterior y querés ver el material tal como se dictó en tu momento, ubicate en el tag correspondiente:

  ```bash
  git fetch --tags
  git checkout tags/2025
  ```

## Quick start

### Prerrequisitos

- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — ver cómo instalarlo abajo

### 1. Instalar uv (si no lo tenés)

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

No hace falta tener Python instalado de antemano: uv descarga la versión que le pidas.

### 2. Clonar el repositorio

```bash
git clone https://github.com/halexisgonzalez/inteligencia-artificial.git
cd inteligencia-artificial
```

### 3. Crear el entorno virtual

```bash
uv venv --python 3.11
```

### 4. Activar el entorno

**Windows (PowerShell):**

```bash
.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 5. Instalar dependencias

```bash
uv pip install -e .
```

### 6. Registrar el kernel en Jupyter

```bash
python -m ipykernel install --user --name=inteligencia-artificial --display-name "Python (IA)"
```

### 7. Abrir Jupyter y ponerse a trabajar

```bash
jupyter notebook
```

Al abrir una notebook, elegí el kernel **"Python (IA)"** desde **Kernel → Change Kernel**.

### Mantenerse actualizado

Cada vez que se publique material nuevo, alcanza con traer los cambios:

```bash
git pull
```

Si se agregan dependencias nuevas a `pyproject.toml`, volvé a correr `uv pip install -e .` para instalarlas.

## Problemas comunes

**`uv: no se reconoce como un comando` después de instalarlo**
El instalador agrega `uv` al PATH, pero las terminales que ya estaban abiertas no se enteran. Cerrá la terminal y abrí una nueva. Si no querés reabrirla, en esa misma sesión de PowerShell corré:

```powershell
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
```

**`.venv\Scripts\activate` falla con un error de "execution policy" en PowerShell**
Windows por defecto no deja correr scripts `.ps1`. Habilitalo solo para esa sesión:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

o activá el entorno desde `cmd.exe` en vez de PowerShell:

```bash
.venv\Scripts\activate.bat
```

**El kernel "Python (IA)" no aparece en Jupyter**
Confirmá que el entorno esté activado antes de registrar el kernel (paso 6 del Quick start) y volvé a correr el comando. Si seguís sin verlo, reiniciá Jupyter (cerrá y volvé a correr `jupyter notebook`).

**`uv pip install -e .` dice que no encuentra el entorno / instala en el Python global**
Es porque el `.venv` no está activado. Activalo (paso 4) y volvé a instalar; se nota porque el prompt de la terminal empieza con `(.venv)`.

**VS Code no encuentra las librerías instaladas**
El editor puede seguir usando otro intérprete de Python. Con la notebook o un `.py` abierto, elegí manualmente el intérprete: `Ctrl+Shift+P` → **Python: Select Interpreter** → el que apunta a `.venv`.

## Bibliografía recomendada

**Libro principal:**

- *Artificial Intelligence: A Modern Approach* — Stuart Russell, Peter Norvig (Ed. Pearson)

**Otros recursos útiles:**

- *Artificial Intelligence Basics: A Non-Technical Introduction* — Tom Taulli (Ed. Apress)
- *Artificial Intelligence For Dummies* — John Paul Mueller, Luca Massaron
- [*An Introduction to Statistical Learning*](https://www.statlearning.com/) — Gareth James et al. (Ed. Springer)
- [*Python Data Science Handbook*](https://jakevdp.github.io/PythonDataScienceHandbook/) — Jake VanderPlas
- *The Elements of Statistical Learning* — Trevor Hastie et al. (Ed. Springer)

## Docente

- **Ing. Alexis González**

## Contacto

Para consultas sobre la cursada, usar los canales oficiales de la materia.

## Licencia

Este material está bajo una licencia [Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es). Podés compartirlo y adaptarlo dando crédito, siempre que no sea con fines comerciales y que compartas cualquier adaptación bajo la misma licencia. Ver el archivo [LICENSE](LICENSE).

---

**¡Bienvenidos a Inteligencia Artificial!**
