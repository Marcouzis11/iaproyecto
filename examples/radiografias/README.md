# Radiografías de ejemplo

Cuatro radiografías PA del **test oficial** de NIH ChestX-ray14, para probar `rx-predecir` sin descargar el dataset. Ninguna se usó para entrenar el modelo ni para elegir su umbral.

Se eligió una al azar de cada celda de la matriz de confusión del modelo B en test (`random.Random(42)` sobre `predicciones_test.csv`), así se ven aciertos y errores. No representan la exactitud del modelo: en test acertó el 74,3%.

| Imagen | Etiquetas de NIH | ¿Tiene Effusion? | Puntaje del modelo B | Decisión (umbral 0,414) | Resultado |
|---|---|---|---|---|---|
| `00022899_024.png` | Consolidation, Effusion, Mass | Sí | 0,940 | Effusion | Verdadero positivo |
| `00004526_023.png` | Cardiomegaly, Effusion | Sí | 0,345 | Sin Effusion | Falso negativo |
| `00000643_006.png` | Pneumothorax | No | 0,575 | Effusion | Falso positivo |
| `00030344_002.png` | No Finding | No | 0,186 | Sin Effusion | Verdadero negativo |

```bash
rx-predecir examples/radiografias/*.png
```

Los puntajes tienen que coincidir con la tabla hasta el tercer decimal; en CPU o MPS pueden variar en el cuarto.

**Fuente:** NIH Clinical Center, [NIH ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC). Wang X. et al., *ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases*, CVPR 2017. Las imágenes están anonimizadas y se redistribuyen con esta atribución.
