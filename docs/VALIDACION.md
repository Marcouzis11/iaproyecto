# Cómo se validó el código y los datos

## Pruebas automáticas

`python -m unittest discover -s tests` corre las pruebas sin necesitar el dataset. Todas usan datos sintéticos, salvo `tests/test_examples.py` y `tests/test_app.py`, que usan el modelo final y las radiografías de ejemplo versionadas, y `tests/test_recompute.py`, que usa las predicciones versionadas de los cuatro modelos:

| Archivo | Qué comprueba |
|---|---|
| `tests/test_preparation.py` | Flujo de punta a punta y repetible con la misma semilla; exclusión de duplicados y etiquetas inválidas; ningún paciente en dos conjuntos; estadísticas calculadas solo con train; lectura de 16 bits y RGBA; filtro de vistas; selección 40/60 y repetición de positivas; conservación del test oficial de NIH. |
| `tests/test_training.py` | Métricas contra cálculos a mano; umbral óptimo igual a una búsqueda exhaustiva; baseline siempre positivo; entrenamiento reproducible que nunca abre test; salidas que no se pisan. |
| `tests/test_evaluation.py` | Bootstrap que remuestrea pacientes enteros; test evaluado con el umbral de validación y una sola vez; comparación pareada, que en validación acepta modelos con otros arrays de las mismas imágenes (por ejemplo, otra resolución) si los dos ya se evaluaron, y rechaza conjuntos con otras imágenes o pacientes. |
| `tests/test_inference.py` | La predicción sobre archivos da los mismos puntajes que los arrays preparados; salida en texto, JSON y CSV; errores claros con archivos inválidos o un modelo inexistente. |
| `tests/test_examples.py` | El modelo B versionado da, sobre las cuatro radiografías de ejemplo, el puntaje documentado hasta el tercer decimal y el umbral 0,414; las cuatro cubren las celdas de la matriz de confusión. |
| `tests/test_recompute.py` | `rx-recalcular` reproduce desde las predicciones versionadas las 7 evaluaciones y las 3 comparaciones, sin diferencias con sus `report.json`; las cifras del README (F1 0,744 con IC 0,726 a 0,761, AUC 0,869, matriz de confusión de B, F1 de A, control y C, 26 falsos positivos menos de C); cada CSV publica imagen, paciente, etiqueta y puntaje con 40% de positivas; ningún paciente está en validación y en test; un `report.json` alterado se detecta. Detecta las dos mutaciones que sobrevivían en la revisión del MVP: el recall de `binary_metrics` y el tamaño de la remuestra del bootstrap. |
| `tests/test_checksums.py` | `rx-verificar-datos` acepta una carpeta idéntica y señala los archivos que faltan o cambiaron; la lista de los datos de B incluye los 14 archivos de la preparación. Los pesos versionados de A, B, control y C tienen el SHA-256 fijado, y cada uno guarda la época y el umbral que figuran en sus reportes de entrenamiento y de validación. |
| `tests/test_app.py` | La página local (`rx-probar`) responde, da los mismos puntajes que `rx-predecir` sobre las radiografías de ejemplo, devuelve la imagen de entrada y el mapa de calor en 224×224, y contesta con un error claro ante un archivo que no es imagen. |

`notebooks/02_pruebas_pipeline.ipynb` repite las pruebas de preparación sobre el código del notebook.

## Comprobaciones sobre NIH

Hechas contra el CSV original, por fuera del código de preparación. Se reproducen en la sección 6 de [`notebooks/00_eda_nih_effusion.ipynb`](../notebooks/00_eda_nih_effusion.ipynb); el detalle está en [`SPLITS_NIH_EFFUSION.md`](SPLITS_NIH_EFFUSION.md).

- 0 pacientes compartidos y 0 imágenes idénticas entre conjuntos.
- Todas las imágenes son PA y cada etiqueta coincide con la original.
- El test contiene solo imágenes de `test_list.txt`.
- 40,0% de positivas en los tres conjuntos.

## Instalación limpia

Antes de la entrega se copió el repositorio a una carpeta nueva, se creó un entorno virtual vacío con Python 3.11 y se instaló con `python -m pip install -e .`; en otra copia, con `python -m pip install -r requirements.txt -e .`. En los dos entornos:

- Pasaron las 46 pruebas.
- `rx-predecir examples/radiografias/*.png` reprodujo los puntajes que el modelo B había dado a esas imágenes en la evaluación de test (0,940, 0,345, 0,575 y 0,186), en MPS y en CPU.
- `scripts/flujo_completo.sh demo` corrió de punta a punta.

Para la entrega del MVP se repitió en Windows 11 con Python 3.13, en entornos nuevos: uno con pip (`python -m pip install -e .`) y otro con uv (`uv pip install -r requirements.txt -e .`). En los dos pasaron todas las pruebas y `rx-predecir` dio en CPU los mismos puntajes (0,940, 0,345, 0,575 y 0,186). Desde entonces, GitHub Actions repite la instalación, las pruebas y `rx-predecir` en Ubuntu y Windows en cada push ([`tests.yml`](../.github/workflows/tests.yml)).
