# Cómo se validó el código y los datos

## Pruebas automáticas

`python -m unittest discover -s tests` corre las pruebas sin necesitar el dataset. Todas usan datos sintéticos, salvo `tests/test_examples.py`, que usa el modelo final y las radiografías de ejemplo versionadas:

| Archivo | Qué comprueba |
|---|---|
| `tests/test_preparation.py` | Flujo de punta a punta y repetible con la misma semilla; exclusión de duplicados y etiquetas inválidas; ningún paciente en dos conjuntos; estadísticas calculadas solo con train; lectura de 16 bits y RGBA; filtro de vistas; selección 40/60 y repetición de positivas; conservación del test oficial de NIH. |
| `tests/test_training.py` | Métricas contra cálculos a mano; umbral óptimo igual a una búsqueda exhaustiva; baseline siempre positivo; entrenamiento reproducible que nunca abre test; salidas que no se pisan. |
| `tests/test_evaluation.py` | Bootstrap que remuestrea pacientes enteros; test evaluado con el umbral de validación y una sola vez; comparación pareada. |
| `tests/test_inference.py` | La predicción sobre archivos da los mismos puntajes que los arrays preparados; salida en texto, JSON y CSV; errores claros con archivos inválidos o un modelo inexistente. |
| `tests/test_examples.py` | El modelo B versionado da, sobre las cuatro radiografías de ejemplo, el puntaje documentado hasta el tercer decimal y el umbral 0,414; las cuatro cubren las celdas de la matriz de confusión. |

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
