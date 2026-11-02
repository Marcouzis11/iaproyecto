# Train, validación y test: NIH ChestX-ray14 · Effusion

**Config:** [`configs/nih.json`](../configs/nih.json) · **Seed:** 42 · **Salida:** `data/processed/nih_effusion_pa_40_60_v1/` (2,8 GB, fuera de git)

**Comando:** `.venv/bin/python -m rx_torax.prepare --config configs/nih.json`

Reemplaza a la versión de Pneumothorax ([`SPLITS_NIH_PNEUMOTHORAX.md`](SPLITS_NIH_PNEUMOTHORAX.md)), que tenía 3,6% de positivos en train y 13,9% en test.

![Particiones, ejemplos e histograma](img/splits_nih_effusion.png)

## Problema
Clasificación binaria sobre radiografías **PA**:
- **1:** la imagen tiene la etiqueta *Effusion*, sola o con otros hallazgos.
- **0:** radiografía PA sin esa etiqueta. Un 0 no significa radiografía normal.

## Conjuntos

| Conjunto | Total | Con Effusion | Sin hallazgos | Otros hallazgos | Pacientes |
|---|---|---|---|---|---|
| **Train** | 9.447 | 3.779 (40%) | 3.684 (39%) | 1.984 (21%) | 6.116 |
| **Val** | 1.667 | 667 (40%) | 650 (39%) | 350 (21%) | 1.078 |
| **Test** | 3.777 | 1.511 (40%) | 1.473 (39%) | 793 (21%) | 1.497 |
| **Total** | **14.891** | **5.957** | **5.807** | **3.127** | **8.691** |

## Datos usados
De las 112.120 filas del CSV:

| Motivo | Filas |
|---|---|
| Vista AP, excluida | 41.575 |
| `images_010` no disponible | 10.000 |
| Imágenes duplicadas, excluidas | 12 |
| **Aceptadas (PA)** | **60.533** |

De las aceptadas se usan todas las positivas (5.957) y una muestra de negativas (8.934). Las demás no se borran: simplemente no entran en los arrays.

**Datos incompletos:** falta `images_010`, porque la carpeta descargada como `images 10` es una copia de `images 12`. Con ese archivo se sumarían 632 Effusion PA (~1.580 imágenes en total).

**Ubicación de las imágenes:** el pipeline las busca dentro de `data/raw/nih/`. Hoy `data/raw/nih/images/` tiene enlaces simbólicos a las carpetas descargadas, sin `images 10`, porque los nombres repetidos se excluyen como ambiguos.

## Flujo aplicado
1. **Selección de vista:** solo PA.
2. **Auditoría:** se abre cada imagen, se detectan ilegibles y duplicados por hash de píxeles.
3. **Split por paciente:** test es el oficial de NIH. Val es el 15% de los pacientes de `train_val_list.txt`.
4. **Selección 60/40 en cada conjunto:** todas las positivas y negativas al azar con seed fija. Las negativas son 65% sin hallazgos y 35% con otros hallazgos (mezcla real en PA), con hasta 3 por paciente.
5. **Transformación:** escala de grises, 224×224 sin deformar (bordes negros) e intensidades en [0, 1].
6. **Estadísticas solo con train:** media 0,510 y desvío 0,265, guardadas en `preprocessing.json` para aplicarlas sin recalcular a val, test e imágenes nuevas.

No se repiten imágenes ni se aplica augmentation en esta etapa.

## Verificaciones
Se validaron contra el CSV original, con un script aparte del pipeline:
- 0 pacientes compartidos y 0 imágenes idénticas entre conjuntos.
- Todas las imágenes son PA, y cada `y` coincide con su etiqueta original.
- Test contiene solo imágenes de `test_list.txt`; train y val, solo de `train_val_list.txt`.
- Están las 5.957 Effusion PA disponibles.
- 40,0% de positivos y 65,0% de negativas sin hallazgos en los tres conjuntos.
- Máximo de 3 negativas por paciente en cada conjunto.
- Edad media con/sin Effusion: 51,2/46,9 años en train y 49,3/47,2 en test. Hombres con/sin Effusion: 53%/54% en train y 55%/56% en test.

## Diferencia con el material de clase
La [notebook de desbalance](../git-profe/06_feature_engineering_avanzado/03_desbalance.ipynb) y el flujo de preparación balancean **solo train**. Acá también se ajustan val y test porque el profesor pidió el mismo porcentaje en train y test. En val y test solo se eligen imágenes: no se repite ninguna ni se generan sintéticas.

**Consecuencia:** la proporción real en PA es ~10% en todo NIH y 14,9% en el test oficial disponible. Con 40%, la precisión y el F1 salen más altos que con esas proporciones. Recall, especificidad y AUC dependen mucho menos de la proporción.

## Limitaciones
- **Dispositivos:** en una muestra chica de 96 fotos, revisada a ojo, se ven cables, catéteres, puertos o implantes en ~30% de las positivas y ~13% de las negativas. NIH no los marca, así que siguen incluidos. El modelo podría aprender esa señal: hay que medirlo en la evaluación.
- **Calidad de imagen:** en una muestra de 4.000 fotos PA, los marcos blancos rondan el 0,3% y el contraste bajo el 1,3%. Se ven legibles, así que no se aplicó ningún filtro.
- **Controles previos:** los pacientes con Effusion tienen más estudios previos, lo que puede agregar señales ajenas al hallazgo.
- **Etiquetas:** NIH las extrajo automáticamente de informes médicos, así que contienen errores.
- **Test oficial:** sus pacientes tienen más estudios por persona que los de train.

## Pendiente para entrenar
- **Modelo A (sacar negativas):** ya se puede entrenar con estos arrays.
- **Modelo B (repetir positivas):** hay que generar un train con más negativas. Val y test deben quedar iguales; la selección usa un generador distinto por conjunto para eso.
