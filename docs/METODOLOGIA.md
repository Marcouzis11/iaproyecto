# Metodología y decisiones

El [README](../README.md) resume el proyecto. Acá están las justificaciones: por qué se tomó cada decisión, con el número o la slide que la respalda. De qué slide o notebook de la cátedra sale cada una, y en qué se aparta, está en [relación con el material de clase](TRAZABILIDAD_CLASES.md).

## Contenido

- [El problema como agente](#el-problema-como-agente)
- [Métricas de éxito y protocolo](#métricas-de-éxito-y-protocolo)
- [Cronología](#cronología)
- [Análisis exploratorio](#análisis-exploratorio)
- [Decisiones y la estadística que las respalda](#decisiones-y-la-estadística-que-las-respalda)
- [Preprocesamiento](#preprocesamiento)
- [Modelo y entrenamiento](#modelo-y-entrenamiento)
- [Validación](#validación)
- [Análisis crítico de los resultados](#análisis-crítico-de-los-resultados)

## El problema como agente

Propiedades del entorno, con las seis dimensiones de clase (slides 07, pp. 42-48):

| Dimensión | Entorno | Por qué |
|---|---|---|
| Observabilidad | Parcialmente observable | Una sola proyección a 224×224, sin historia clínica y con etiquetas ruidosas |
| Determinismo | Determinista | La misma imagen da siempre el mismo puntaje; la incertidumbre está en las etiquetas |
| Episodicidad | Episódico | Cada estudio se decide solo y no condiciona al siguiente |
| Dinamismo | Estático | La imagen no cambia mientras el agente decide |
| Continuidad | Percepción continua, acción discreta | Píxeles y puntaje continuos; la decisión tiene dos clases |
| Agentes | Individual | No hay otros agentes en el entorno |

Es un agente que aprende durante el entrenamiento (p. 54); en uso es un agente reactivo simple (p. 50), con la regla "si el puntaje es ≥ 0,414, Effusion".

## Métricas de éxito y protocolo

- **Métrica principal:** F1-Score de la clase positiva. La consigna lo da como ejemplo; lo elegimos porque, con 40% de positivos, no se infla como la exactitud.
- **Costo de los errores:** F1 pesa igual una falsa alarma que un derrame perdido, pero para priorizar estudios perder un derrame es más grave (slides 09, p. 10). Por eso se informa también el recall y un punto de operación con recall ≥ 95%, elegido en validación: umbral 0,136, especificidad 59,5% (en validación).
- **Meta de referencia:** F1 > 0,80, el ejemplo de la consigna.
- **Baseline sin IA:** hoy se leen todas las radiografías, que equivale a marcarlas todas como positivas: F1 0,571 con 40% de positivos (recall 100%, precisión 40%). Marcarlas todas como negativas da F1 0.
- **Protocolo:** el umbral y el modelo se eligen en validación; el test se evalúa una sola vez. La época y el modelo se eligen por AUC de validación, que no depende del umbral; con el F1 de validación la elección habría sido la misma (B 0,800, A 0,795).

## Cronología

La consigna pide el Charter antes de codificar (p. 3). La primera propuesta es del 18/10 ([`PLAN_INICIAL.md`](PLAN_INICIAL.md)) y se rehízo el 21/10. El problema final, *Effusion* con 40% de positivos, se definió el 01/11 después del EDA. A y B se entrenaron y evaluaron el 2 y el 3/11. El F1 como métrica de éxito quedó escrito el 4/11, antes de evaluar el modelo C; el Charter con PEAS se completó el 10/11. Para A y B, el 0,80 se adoptó como referencia después de evaluar; para C se fijó antes.

## Análisis exploratorio

- **Pacientes:** el 84% de las radiografías es de pacientes con más de un estudio, y las de una misma persona se parecen. Por eso se separa por paciente.
- **Desbalance:** solo el 9,8% de las PA tiene Effusion (15,8% en el test oficial); entropía de Shannon 0,46 e índice de Gini 0,18 (slides 05, p. 7). Por pedido del profesor, train, validación y test tienen 40% de positivos (Shannon 0,97, Gini 0,48). En clase se balancea solo train (slides 06, pp. 29, 31 y 35), así que precisión y F1 salen más altos que con la proporción real: ver [análisis crítico](#análisis-crítico-de-los-resultados).
- **Vistas:** 44.810 radiografías son AP. Suelen ser placas portátiles de pacientes en cama. Con las medidas de asociación de clase (slides 04, p. 47), la vista casi no se asocia con Effusion (φ = 0,08, despreciable) pero sí con tener 10 o más estudios previos (φ = 0,28, débil): son otra población, así que se excluyeron.
- **Primer intento descartado:** con *Pneumothorax* había 3,6% de positivos en train y 13,9% en test, demasiado pocos. Se cambió a *Effusion* ([resumen](SPLITS_NIH_PNEUMOTHORAX.md)).
- **Archivos:** al auditar la descarga apareció una carpeta `images_010` que era copia de otra; se volvió a bajar.
- **Edad y sexo:** parecidos entre positivas y negativas (edad media 51 contra 47 años en train; 54–55% hombres en los dos grupos). Correlación punto biserial de la edad 0,15 (débil) y φ del sexo 0,005 (despreciable): no se balancea por ellas.
- **Estudios previos:** punto biserial 0,25 con Effusion en train (moderada). Es un posible atajo, que después se midió en el modelo.
- **Dispositivos:** en una muestra revisada a ojo, se ven cables o catéteres en ~30% de las positivas y ~13% de las negativas.
- **Faltantes y outliers:** el CSV no tiene faltantes (0 en las 11 columnas). Con IQR y ±3σ (slides 04, pp. 50-51) sobre el brillo y el contraste de cada imagen de train se marcan placas lavadas, sobreexpuestas o con bordes negros, en proporción parecida en las dos clases: son placas legítimas y se conservan. Apareció un solo error, una placa lateral etiquetada como PA (`00008347_002.png`, negativa de train), que quedó documentado.

Todo este análisis, con sus tablas y gráficos y la decisión que sale de cada uno, está en el notebook [`00_eda_nih_effusion.ipynb`](../notebooks/00_eda_nih_effusion.ipynb), que se ve con sus resultados directamente en GitHub. El detalle de los conjuntos está en [train, validación y test](SPLITS_NIH_EFFUSION.md).

## Decisiones y la estadística que las respalda

| Decisión | Estadística que la respalda | Notebook 00 |
|---|---|---|
| Separar por paciente | El 84% de las radiografías es de pacientes con más de un estudio | Sección 1 |
| Usar solo PA | Vista AP × Effusion: φ = 0,08, despreciable. Vista AP × 10 o más estudios previos: φ = 0,28, débil. AP es otra población, no un problema de prevalencia | Sección 3 |
| Effusion como hallazgo | 6.589 positivas PA, la segunda cantidad después de Infiltration (9.353), que es una etiqueta poco específica. Pneumothorax se descartó: 3,6% de positivas en train contra 13,9% en test | Sección 4 |
| 40% de positivas en los tres conjuntos | Pedido del profesor. La proporción real es 9,8% (Shannon 0,46, Gini 0,18); con 40%, Shannon 0,97 y Gini 0,48. Con la proporción real, el F1 de B sería 0,34 | Secciones 2 y 6 |
| Negativas: 65% sin hallazgos y 35% con otros | Es la mezcla de las negativas PA: 64,7% en todas, 67,1% solo en `train_val` | Sección 5 |
| Máximo 3 negativas por paciente | El 14% de los pacientes aporta el 47% de las negativas: sin tope, pocos pacientes dominarían la clase | Sección 5 |
| No balancear por edad ni sexo | Edad × Effusion: punto biserial 0,15, débil. Sexo × Effusion: φ = 0,005, despreciable (p = 0,60) | Sección 7 |
| Vigilar los estudios previos como atajo | Estudios previos × Effusion: punto biserial 0,25, moderada; Spearman 0,32. Solos separan las clases con AUC 0,68 | Sección 7 |
| Cortes de estudios previos 0 / 1-9 / 10 o más | Cortes fijos por dominio; 10 queda justo por encima del tercer cuartil de las positivas de train (9) | Sección 7 |
| Conservar los outliers de imagen | Con IQR, el contraste marca 7,5% de las positivas y 7,9% de las negativas: proporción parecida, placas legítimas | Sección 8 |
| Edad con media; estudios previos con mediana e IQR | Asimetría de la edad −0,28 (simétrica); de los estudios previos 4,24 (muy asimétrica) | Sección 1 |
| Validación = 15% de los pacientes de `train_val` | 1.813 imágenes con 725 positivas: alcanza para elegir época y umbral (IC del F1 de ±0,03) sin restarle mucho a train | `configs/nih.json` |
| z-score con media 0,511 y desvío 0,263 | Calculados solo con los píxeles de train y aplicados igual al resto | `preprocessing.json` |
| Época de cada modelo | Máximo AUC de validación; se corta tras 4 épocas sin mejora | `historial.csv` |
| Umbral 0,414 | Máximo F1 en validación (0,800, contra 0,798 con 0,5) | `report.json` |
| Modelo B sobre A | Mayor AUC de validación (0,905 contra 0,898); la diferencia no es significativa con α = 0,05 | `comparacion_val_a_b` |
| Intervalos por paciente | En test hay 2,6 imágenes por paciente: no son observaciones independientes | `evaluate.py` |

## Preprocesamiento

1. **Limpieza:** de 112.120 filas se excluyen 44.810 AP y 12 duplicadas por hash de píxeles: 3 copias exactas del mismo paciente (se conserva una) y 9 entre pacientes distintos (se excluyen todas). Quedan 67.298 PA.
2. **Separación por paciente:** test es la lista oficial de NIH. Validación es el 15% de los pacientes de `train_val_list.txt`. Ningún paciente ni imagen se repite entre conjuntos.
3. **40% de positivas:** se usan todas las positivas y se eligen negativas al azar con semilla fija: 65% sin hallazgos y 35% con otros, y como máximo 3 por paciente. La mezcla y el tope se aplicaron en los tres conjuntos, y el 65% se tomó de todas las negativas PA, test incluido (solo con `train_val` da 67%). En clase, lo que se calcula sale de train y en test solo se aplica (slides 06, pp. 30-31): el efecto sobre los resultados está en el [análisis crítico](#análisis-crítico-de-los-resultados).
4. **Transformación:** escala de grises, 224×224 conservando la proporción con bordes negros (interpolación bilineal de Pillow, que suaviza al reducir), valores en [0, 1]. La media (0,511) y el desvío (0,263) se calculan **solo con train** (slides 10, p. 22) y se aplican igual a validación, test e imágenes nuevas. Se estandariza en lugar de dejar [0, 1], que es lo que sugiere slides 06 p. 19 para redes neuronales, porque la DenseNet121 preentrenada espera entradas centradas; se usan las estadísticas de train y no las de ImageNet porque las radiografías tienen otra distribución. No se aplican filtros de ruido: la red aprende sus propios filtros, y suavizar podría borrar detalles de los ángulos costofrénicos.
5. **Aumento de datos, solo en train:** rotación ±7°, escala ±5% y desplazamiento ±5%. Sin espejar, porque el corazón está a la izquierda.

## Modelo y entrenamiento

**DenseNet121 preentrenada en ImageNet**, con la última capa reemplazada por una sola salida. Es la arquitectura de CheXNet, un trabajo de referencia sobre este mismo dataset, y la transferencia de aprendizaje permite entrenar con 7.252 a 22.594 imágenes en lugar de millones.

- **Por qué una CNN y no los clasificadores de clase:** KNN, SVM o árboles (slides 01, p. 47) sobre píxeles tendrían 50.176 valores por imagen, no toleran desplazamientos y comparar contra todo train es costoso. Las redes y las CNN están en el programa de la materia (slides 00, p. 8). En el MVP no se probó otra red porque cada entrenamiento lleva de 30 a 79 minutos y el cómputo se usó para comparar cómo armar train; es una de las [mejoras para el final](MEJORAS_FINAL.md).
- **Parámetros contra datos:** DenseNet121 tiene unos 7 millones de parámetros, muchos más que imágenes de train, al revés del criterio de slides 09, p. 28. Lo compensan partir de los pesos de ImageNet, el aumento de datos y el early stopping; aun así sobreajusta rápido (mejor época entre la 1 y la 4).

Entrenamiento: pérdida BCE, AdamW (lr 1e-4, weight decay 1e-4), lotes de 32, hasta 15 épocas con early stopping por AUC de validación (paciencia 4). El learning rate se multiplica por 0,3 cuando el AUC de validación no mejora en dos épocas seguidas. Semilla 42 en el split, la inicialización y el aumento de datos.

Los hiperparámetros no se buscaron comparando en validación, como se hace en clase (slides 09, p. 38): son valores habituales para ajustar redes preentrenadas, con un learning rate chico para no pasarse del mínimo (slides 08, pp. 25-26), y una búsqueda habría multiplicado entrenamientos de 30 a 79 minutos. Lo que sí se elige en validación es la época y el umbral.

Las cuatro formas de llegar a 40% de positivas en train, con sus tiempos en una Mac M4 con MPS, están en el README; las configuraciones, en [`configs/`](../configs/).

## Validación

- **Train** ajusta los pesos; **validación** elige la época, el umbral (maximizando F1) y el modelo final; **test** se usa una sola vez con todo fijado. `rx-evaluar` se niega a evaluar dos veces el mismo conjunto.
- **Validación única, no k-fold:** cada entrenamiento tarda de 30 a 79 minutos; con 5 folds por paciente serían de 2,5 a 6,5 horas por modelo. Con procesos lentos y datos grandes conviene una sola validación (slides 09, p. 46). La contracara es que depende de la partición (p. 39), y se vio: la validación, sacada de `train_val`, no anticipó la población del test oficial.
- **Intervalos de confianza:** bootstrap de 2.000 remuestreos **por paciente**, porque las imágenes de un mismo paciente no son independientes. Miden la incertidumbre del conjunto evaluado, no la variación entre entrenamientos: hay una sola corrida por modelo. Repetir B con 3 semillas es otra de las [mejoras para el final](MEJORAS_FINAL.md).
- **Comparaciones como test de hipótesis** (slides 04, pp. 11-12 y 19): H0 dice que la diferencia entre dos modelos es 0 y H1 que no lo es, con α = 0,05 fijado de antemano. Se rechaza H0 si el IC 95% pareado de la diferencia no incluye el 0. Si lo incluye, no hay evidencia suficiente de una diferencia, lo que no prueba que los modelos sean iguales.
- **Decisión previa:** antes de abrir el test se eligió B, por tener el mayor AUC de validación. A no se evaluó en test para que el resultado no influyera en la elección. La decisión se versionó junto con los resultados; el orden consta en los reportes: la comparación A-B es de las 13:19 UTC del 3/11 y la evaluación de test, de las 13:26.

## Análisis crítico de los resultados

- **El modelo aprende algo real:** AUC 0,87 en pacientes que nunca vio, y el intervalo del F1 queda entero por encima del baseline.
- **No alcanza el 0,80 que la consigna da como ejemplo.** En validación B daba justo 0,800, pero en test cae a 0,744. La especificidad baja de 81% a 62%: el modelo da muchas falsas alarmas.
- **Parte de la caída se explica por la población.** El test oficial tiene muchos más pacientes con 10 o más estudios previos, y ahí la especificidad es 35%. Con la mezcla de validación, la especificidad de test sería 69% en vez de 62%; el resto es una caída dentro de cada grupo.
- **El modelo usa en parte la señal "paciente internado".** El número de estudios previos solo, sin mirar la imagen, ya separa las clases con AUC 0,73. Medido con la correlación de Spearman (slides 03, p. 50): entre las negativas, el puntaje sube con los estudios previos (ρ = 0,49, IC 95% 0,45 a 0,52, en test; 0,26 en validación); entre las positivas no hay relación (ρ = −0,03, IC −0,08 a 0,03).
- **A contra B:** no se detectó una diferencia significativa en F1 ni en AUC (los IC de la diferencia incluyen el 0). B detecta más (recall +4,1 puntos) a cambio de más falsos positivos.
- **El modelo C confirmó la hipótesis a medias.** Entrenar con negativas parecidas a las del test bajó los falsos positivos de forma significativa (−26, especificidad +3,3 puntos), pero el F1 no mejoró de forma significativa (0,784 contra 0,775 del control). Con AUC ~0,90, ni el mejor umbral posible pasa de 0,80: hace falta un modelo que separe mejor.
- **El F1 depende de la proporción de positivos.** Con el mismo recall y especificidad, en la proporción real de NIH PA (9,8%) el F1 sería 0,34 y la precisión 21%: 4 de cada 5 alarmas serían falsas. Sirve, como mucho, para priorizar estudios. Además, 0,414 es el umbral óptimo para 40% de positivos: con 9,8%, reponderando validación, el óptimo sería ~0,77. Se elegiría así, en validación, nunca con test.
- **El test preparado es más fácil que el oficial completo.** Sus negativas son 65% sin hallazgos y con máximo 3 por paciente; en el test oficial son 51% y sin tope. Reponderando la especificidad de B por grupo a la mezcla natural (análisis posterior, sin cambiar el modelo ni el umbral):

| Mezcla de negativas | Especificidad | F1 con 40% de positivos | F1 con 15,8% |
|---|---|---|---|
| Test preparado | 61,8% | 0,744 | 0,470 |
| Natural, por tipo de negativa | 58,7% | 0,730 | 0,451 |
| Natural, por tipo y estudios previos | 54,2% | 0,711 | 0,426 |

El análisis completo está en [resultados de A y B](RESULTADOS_MODELOS.md), [modelo C](MODELO_C.md) y el [informe en PDF](Informe_proceso_Effusion.pdf).
