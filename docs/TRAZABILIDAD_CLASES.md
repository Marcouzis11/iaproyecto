# Decisiones del proyecto y material de la cátedra

De qué slide, notebook o página de la consigna sale cada decisión, si se hizo como en clase y qué conviene corregir.

**Cómo se revisó:** se leyeron los 12 PDF de `Slides/` página por página, incluidas las láminas que son solo imagen, la consigna (`IA___TPFinal.pdf`, igual a `consigna.pdf`) y los notebooks de `git-profe/`. Se controlaron 216 citas contra la página real: 210 se confirmaron, 3 tenían la página o la celda corrida (acá van corregidas) y 3 se descartaron porque no respaldaban la decisión. Las cifras se recalcularon con los datos y el código del repositorio.

**Referencias:**

- **S06 p. 29:** `Slides/06 - Procesamiento y nuevas features.pdf`, página 29 del PDF. **EXTRA** es `Slides/EXTRA - Computer Vision I.pdf`.
- **nb 06/03_desbalance c. 14:** `git-profe/06_feature_engineering_avanzado/03_desbalance.ipynb`, celda 14 contando desde 0.
- **Consigna p. 3:** página del PDF de la consigna.
- **Plantilla:** `git-profe/trabajo_final/plantilla/README.md`.

| Estado | Significa |
|---|---|
| **Conforme** | Se hizo como en clase. |
| **Adaptado** | Misma idea que en clase, con una variante justificada. |
| **Difiere** | Se aparta del material: hay que explicarlo en la defensa. |
| **Fuera del material** | No se vio en clase; se indica de dónde sale. |

## Resumen

48 decisiones. Antes de las correcciones del 12/11: 13 conformes, 24 adaptadas, 5 que diferían y 6 fuera del material. Ahora: **17 conformes, 29 adaptadas, 1 que difiere y 1 fuera del material.**

- **Lo central sigue al material:** split antes de transformar, media y desvío solo de train, balanceo de train, validación para elegir época, umbral y modelo, y test evaluado una sola vez.
- **Las estadísticas del EDA usan las medidas de clase:** Phi, punto biserial, Spearman, χ² con α = 0,05, Shannon y Gini, IQR y ±3σ (sección 9).
- **Lo que se aparta de clase está documentado y medido:** 40% en validación y test (pedido del profesor), la mezcla de negativas en test (especificidad reponderada) e hiperparámetros sin búsqueda (justificado).
- **Sigue fuera del material:** DenseNet121 y la transferencia de aprendizaje, que el programa anuncia pero no tienen deck publicado.
- **Sigue difiriendo, y depende del equipo:** horas en los commits, acceso del docente al repositorio e issues (sección 12).

## 1. Planteo, consigna y organización

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| A1 | Clasificación binaria supervisada: puntaje de 0 a 1 y clase según un umbral fijado en validación | S02 p. 7 (clasificación) y p. 15 (ejemplo de visión artificial); S09 p. 21 (clasificación binaria y frontera de decisión); S01 p. 23 (radiografía de tórax como caso de ML) y pp. 36-43 (dos clases, probabilidad de riesgo, frontera); S09 pp. 38-39 (decidir en validación) | **Conforme** |
| A2 | PEAS en el README | Consigna p. 3 (Charter con PEAS antes de codificar); S07 pp. 40-41 (PEAS y ejemplos) y p. 45 (entorno episódico: el ejemplo es un clasificador de imágenes médicas) | **Adaptado:** el PEAS ya caracteriza las seis dimensiones del entorno (S07 pp. 42-48) y el tipo de agente (pp. 50 y 54). Se escribió después de entrenar; el README lo cuenta en la cronología del Charter |
| A3 | F1 como métrica principal, 0,80 como referencia, baselines sin IA | Consigna p. 3 (F1 > 0,80 como ejemplo y baseline sin IA) y p. 12 (rúbrica); plantilla, Resultados (justificar F1 o AUC con desbalance; tabla contra baseline); S05 pp. 6-7 (con desbalance los errores se concentran en la clase minoritaria) | **Conforme.** El README aclara que la consigna da el F1 como ejemplo y que F1 pesa igual los dos errores (S09 p. 10) |
| A4 | Fuera de alcance explícito | Consigna p. 4 | **Conforme.** Qué se excluye (AP, multietiqueta, DICOM) sale del EDA |
| A5 | Capas, ramas y PR, venv con versiones fijas, semilla 42, README de la plantilla, licencia MIT | Consigna p. 3, p. 5 y pp. 10-12; S00 pp. 10-11; S01 p. 72 y pp. 77-79; nb 09/01_scikit_learn c. 43-44 (`random_state=42`); `git-profe/trabajo_final/README.md` | **Difiere en tres puntos que dependen del equipo:** los commits no dicen las horas (consigna pp. 10-11), el repositorio es privado y el docente no es colaborador, y no hay issues (rúbrica, p. 12) |
| A6 | MVP `rx-predecir`, 46 pruebas, `flujo_completo.sh` | Consigna p. 4 (el ejemplo de MVP es un script de consola que recibe una imagen y devuelve JSON); S00 p. 4; nb 09/01_scikit_learn c. 63-68 y nb 10/01_regresion_simple c. 51-55 (guardar, cargar y predecir con las mismas versiones) | **Adaptado:** versionar `modelo.pt` es decisión del equipo (la plantilla sugiere no subir modelos pesados); unittest en lugar de pytest (consigna p. 8) |

## 2. Datos, EDA y limpieza

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| B1 | NIH ChestX-ray14; Effusion = 1 si aparece entre las etiquetas | Consigna p. 3 (describir volumen, variables y sesgos); S05 p. 14 (separar texto con split), p. 28 (variable binaria en una columna 0/1) y p. 40 (multietiqueta); S01 p. 43; plantilla, El dataset | **Conforme** |
| B2 | Desbalance: 9,8% de Effusion en PA; co-ocurrencia con otros hallazgos | S05 p. 6 (causas) y p. 7 (detectarlo con gráficos, frecuencias e índices); S06 p. 25; S03 p. 63 (tabla de contingencia) | **Conforme:** proporciones, gráficos e índices de Shannon y Gini (sección 9) |
| B3 | Solo PA | S04 pp. 36-37 (Phi y su escala) y p. 47 (qué medida usar según las variables); nb 03/02_eda_titanic c. 88 (contingencia normalizada por filas); S03 p. 64 | **Conforme:** decidido con Phi (sección 9): AP casi no se asocia con Effusion pero sí con los estudios previos; se excluye por ser otra población |
| B4 | No balancear por edad ni sexo | S04 p. 47, pp. 38-39 (punto biserial) y p. 37 (Phi); S03 p. 61 (comparar una variable numérica entre grupos); nb 04/01_medidas_asociacion c. 10 y c. 13 | **Conforme:** punto biserial de la edad (débil) y Phi del sexo (despreciable) en el notebook 00, sección 7 |
| B5 | Estudios previos (`Follow-up #`) como posible atajo | S04 p. 39 (punto biserial); S03 p. 50 (Spearman y Kendall ante asimetría y outliers); S06 p. 46 (comparar train y test) | **Conforme:** punto biserial 0,245 (moderada) y Spearman 0,321; el AUC 0,684 queda como medida extra |
| B6 | EDA de imágenes: tamaños, modos, ejemplos, histogramas, imagen promedio, contraste | S06 p. 48 y p. 51; nb 06/09_eda_imagenes c. 1 y c. 3 (submuestra de 100 imágenes); EXTRA p. 24 | **Conforme.** La imagen promedio por clase es propia |
| B7 | No se filtran imágenes por calidad ni se borran outliers | S05 p. 24 (decidir si un outlier es un error o un valor legítimo); nb 04/03_eda_ejemplo_smn c. 111 (se conservan los outliers reales); S04 pp. 50-51 (IQR y ±3σ) | **Conforme:** IQR y ±3σ sobre el brillo y el contraste de train (notebook 00, sección 8); los casos marcados se miran y se conservan como valores legítimos, como en el ejemplo del profesor |
| B8 | Auditoría de archivos ausentes o ilegibles; no se imputa | S05 p. 17 y p. 20; nb 02/01_carga_y_exploracion_datos c. 33; plantilla, Metodología | **Conforme:** el notebook 00 cuenta los faltantes del CSV (0 en las 11 columnas); los archivos ausentes o ilegibles van a la auditoría |
| B9 | Duplicados por hash de píxeles | S05 pp. 11 y 13; nb 02/01_carga_y_exploracion_datos c. 34; consigna p. 12 (evitar la fuga de datos); S06 p. 5 | **Adaptado:** se excluyen todas las copias entre pacientes, porque dos grupos tenían copias en train y en test |
| B10 | Effusion en lugar de Pneumothorax | S05 p. 9 (misma proporción de clases en train y test); nb 05/01_split_y_stratify c. 12; S05 p. 7 | **Adaptado.** Por parecido entre listas gana Infiltration; Effusion gana por el tamaño del test y por ser un hallazgo más específico |
| B11 | Dispositivos (cables, catéteres) documentados como riesgo | Consigna p. 3 (describir sesgos); S06 p. 51 (inspección visual) | **Adaptado:** los dispositivos no están anotados, pero el atajo "paciente internado" se midió con Spearman sobre los puntajes (sección 10). La idea de atajo sale de la literatura (Zech et al., 2018) |

## 3. Particiones y desbalance

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| C1 | Split antes de cualquier estadística o transformación | S06 p. 5 y pp. 28-31; S10 pp. 21-22; S05 p. 15; nb 06/04_tratamiento_datos_faltantes_avanzado c. 22 (se ajusta en train y se aplica en test) | **Adaptado:** el código calcula todo con train. La excepción, el 65% y el tope de 3 tomados de todas las PA, está documentada y su efecto, medido (sección 10) |
| C2 | Split por paciente | S09 p. 19 (medir en entradas nunca vistas); S06 pp. 4-5; S05 p. 9 (un split que respeta la estructura de los datos, como en series temporales); consigna p. 12 | **Adaptado:** en clase se dividen filas con `train_test_split`. Por paciente es la práctica estándar en imágenes médicas |
| C3 | Test oficial de NIH; validación = 15% de los pacientes de `train_val_list.txt`, buscando proporciones parecidas | S09 pp. 38-39 y p. 46; S05 p. 9 (split estratificado); nb 05/01_split_y_stratify c. 11; nb 09/01_scikit_learn c. 46; consigna p. 5 | **Adaptado:** `stratify` no respeta pacientes |
| C4 | 40% de positivas en validación y test | S06 p. 29 y p. 35 (en el flujo, Balancear está tachado del lado de test); S06 p. 31 (la columna de test tiene un guion); nb 06/03_desbalance c. 14-15 (sobremuestreo y submuestreo solo sobre `X_train`) | **Adaptado:** pedido del profesor (commit 44776b8), que no está en la consigna escrita. Se documenta la diferencia con clase y se cuantifica el efecto: F1 con la prevalencia real, umbral óptimo para otra prevalencia |
| C5 | Negativas 65% sin hallazgos y 35% con otros; máximo 3 por paciente | S06 p. 26 (submuestreo); nb 06/03_desbalance c. 15 (`RandomUnderSampler(random_state=42)`) | **Adaptado:** la mezcla y el tope se aplicaron también a validación y test, y el 65% salió de todas las PA (S06 pp. 30-31 calcula solo con train). Está documentado y la especificidad se reponderó a la mezcla natural (sección 10) |
| C6 | Cada positiva 3 veces por época, solo en train (modelo B) | S06 p. 26 (sobremuestreo por duplicación) y p. 31 (solo en train); nb 06/03_desbalance c. 14 | **Conforme.** Es una replicación fija ×3, no un sorteo |
| C7 | Modelo C y control con un test nuevo | S09 pp. 38-39; nb 10/03_seleccion_de_modelo c. 6 y c. 23 (el test no se usa para elegir) | **Adaptado:** diseño propio, motivado por los errores de B |

## 4. Preprocesamiento

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| D1 | Grises; intensidades divididas por 255 (o 65535 en 16 bits) | S10 p. 21 (llevar a [0, 1] con el mínimo y el máximo de train); S06 p. 34 (valores de test fuera del rango de train); nb 06/09_eda_imagenes c. 1 (pasar a grises); EXTRA p. 24 y pp. 39-40 | **Adaptado:** usa los límites del formato en lugar del mínimo y el máximo de train. No estima nada, así que no hay fuga ni valores fuera de rango |
| D2 | 224×224 conservando la proporción, con bordes negros e interpolación bilineal | S02 p. 15 (llevar todas las imágenes a un tamaño fijo); S06 p. 51 (estandarizar tamaños); `git-profe/extra/computer_vision/01_introduccion_opencv.ipynb` c. 31 (interpolación bilineal) | **Adaptado:** 224 es la entrada de DenseNet121; los bordes negros son decisión propia |
| D3 | z-score con media 0,508 y desvío 0,265 de train | S10 p. 22 (media y desvío solo de train); S06 p. 29 (calcular en train, aplicar en test); S06 p. 5; nb 10/02_regresion_multiple c. 40 (`StandardScaler` sobre `X_train`) | **Adaptado:** el principio es el de clase y está verificado (sección 10). Un único par para todos los píxeles; el README justifica estandarizar frente a [0, 1] (S06 p. 19) por la convención de las redes preentrenadas |
| D4 | Aumento de datos solo en train: rotación ±7°, escala y desplazamiento ±5%, sin espejar | nb 06/09_eda_imagenes c. 1 (lo nombra); S06 p. 31 (por analogía: lo que agrega muestras va solo en train) | **Adaptado:** el aumento de datos está nombrado en el notebook de EDA de imágenes y va solo en train, como el sobremuestreo (S06 pp. 26 y 31). Las magnitudes son propias; sin espejado por anatomía |
| D5 | La misma transformación en inferencia, con la media y el desvío dentro de `modelo.pt` | S06 pp. 29-31; nb 10/02_regresion_multiple c. 45-46 y c. 68 (se guarda el Pipeline completo); nb 10/03_seleccion_de_modelo c. 29; consigna p. 4 | **Conforme** |

## 5. Modelo y entrenamiento

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| E1 | DenseNet121 preentrenada en ImageNet, con una salida | Ningún deck publicado enseña CNN: S00 p. 8 las anuncia en el programa y S05 p. 30 deja lo preentrenado para deep learning. S09 p. 17: el espacio de hipótesis se elige también por conocimiento previo | **Fuera del material:** el programa anuncia CNN (S00 p. 8) pero no hay deck publicado. Sale de CheXNet (Rajpurkar et al., 2017) y DenseNet (Huang et al., 2017); el README explica por qué no KNN, SVM ni árboles (S01 p. 47) |
| E2 | BCE, AdamW, learning rate 1e-4, weight decay 1e-4, lotes de 32 | S08 pp. 25-26 (descenso por gradiente; elegir α es crítico); S09 p. 38 (los hiperparámetros se eligen comparando en validación); S10 pp. 41-43 (fuerza de la regularización); nb 10/04_regularizacion c. 16 (grilla de α elegida con validación cruzada) | **Adaptado:** los valores no se buscaron en validación; el README lo justifica por costo y con el criterio de α chico (S08 pp. 25-26). Lo que sí se elige en validación es la época y el umbral |
| E3 | Hasta 15 épocas; early stopping por AUC de validación (paciencia 4); learning rate × 0,3 en meseta | S09 p. 39 (validación para detectar sobreajuste en cada iteración); nb 08/06_busqueda_continua c. 9 (α puede empezar alto e ir bajando) | **Adaptado:** valores propios. Corregido en el README y el Informe: el learning rate baja después de dos épocas seguidas sin mejora |
| E4 | Semilla 42 en todo lo aleatorio; `report.json` con configuración y versiones | Consigna p. 5 y p. 12; nb 09/01_scikit_learn c. 43-44 | **Adaptado:** en GPU o MPS el entrenamiento no es determinista, y está aclarado |
| E5 | Sobreajuste leído en las curvas de pérdida de train y validación | S09 p. 28 (rinde en train y no en evaluación), p. 36 (error contra complejidad), p. 37 y p. 39; nb 09/01_scikit_learn c. 63 | **Conforme** |
| E6 | B elegido sobre A por la AUC de validación, antes de abrir test | S09 p. 38 y p. 45; nb 10/03_seleccion_de_modelo c. 23 | **Adaptado:** el bootstrap pareado no se vio en clase; la comparación se plantea como test de hipótesis (S04) |

## 6. Umbral, métricas y errores

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| F1 | Umbral que maximiza F1 en validación (B: 0,414) | S09 pp. 38-39 (se elige en validación); nb 10/04_regularizacion c. 16 (búsqueda en grilla sin tocar el conjunto de evaluación); EXTRA pp. 69-74 (Otsu: probar todos los umbrales posibles y quedarse con el mejor, p. 72); consigna p. 3 | **Adaptado.** Además se informa un punto de operación con recall ≥ 95% elegido en validación (S09 p. 10) y que el óptimo cambia con la prevalencia |
| F2 | Matriz de confusión, precisión, recall, especificidad, F1 | S05 p. 7 (matriz de confusión); nb 09/01_scikit_learn c. 59-62 (exactitud, la única métrica de clasificación de los notebooks); nb 06/03_desbalance c. 1 (la exactitud engaña con desbalance); plantilla | **Adaptado:** las demás métricas son las estándar |
| F3 | AUC por rangos y curva ROC | Solo la plantilla las nombra | **Adaptado:** la plantilla la pide con clases desbalanceadas; el cálculo por rangos es el estándar (Hanley y McNeil, 1982) |
| F4 | Siempre positivo y siempre negativo como referencia | Consigna p. 3; plantilla; nb 10/02_regresion_multiple c. 63-67 (modelo base que predice la media de train) | **Conforme** |
| F5 | Precisión y F1 esperados con la prevalencia real | S05 p. 9 y S06 p. 31 (test conserva la proporción real); S05 p. 6 | **Adaptado:** aplica el principio de clase de que test conserva la proporción real (S05 p. 9; S06 p. 31) con el teorema de Bayes |
| F6 | Subgrupos y casos más seguros de cada celda de la matriz | S05 p. 7 (dónde se concentran los errores); nb 10/05_regresion_no_lineal c. 36 (revisar casos y si el test es representativo); plantilla, análisis crítico | **Adaptado.** Faltan intervalos de confianza por subgrupo |

## 7. Protocolo de validación

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| G1 | Train, validación y test; test una sola vez; sin k-fold | S09 p. 39 (conjunto de validación) y p. 46 (con entrenamientos lentos y datos grandes conviene una validación única); S09 p. 38 y p. 45; nb 10/03_seleccion_de_modelo c. 23 | **Conforme:** el README explica por qué validación única y no k-fold (S09 pp. 39 y 46) |
| G2 | IC 95% por bootstrap de 2.000 remuestreos de pacientes | S04 p. 12 (95% de confianza); S04 p. 14, p. 21 y p. 26 (el procedimiento depende de que las observaciones sean independientes); S03 p. 34 (percentiles) | **Adaptado:** IC 95% como en S04 p. 12, con bootstrap por paciente porque las imágenes no son independientes (S04 p. 21). El bootstrap percentil (Efron) está en *An Introduction to Statistical Learning*, de la bibliografía del curso |
| G3 | Comparación pareada: significativa si el IC de la diferencia no incluye 0 | S04 pp. 11-12 (H0, H1 y α fijado antes), p. 19 (no rechazar H0 no prueba que sea cierta) y p. 32 (t de Student para comparar medias) | **Adaptado:** planteado como test de hipótesis, con H0, H1 y α = 0,05 fijado antes (S04 pp. 11-12); "no rechazar H0" ya no se redacta como "empatan" (p. 19). Usa bootstrap pareado en lugar de t de Student |
| G4 | Criterio de éxito fijado antes de abrir test; test nuevo para C | Consigna p. 3; S04 p. 11; S09 pp. 38-39 | **Adaptado:** para C, sí. Para A y B el 0,80 se adoptó después de evaluar; el README lo dice y el orden de ejecución consta en los reportes |

## 8. Persistencia y MVP

| | Decisión | Dónde se vio | Estado |
|---|---|---|---|
| H1 | `modelo.pt` con pesos, umbral, media, desvío, tamaño y objetivo | nb 10/02_regresion_multiple c. 68 (se guarda el Pipeline completo); nb 10/01_regresion_simple c. 51 (mismas versiones al cargar); nb 09/01_scikit_learn c. 63-68; plantilla `AGENTS.md`, sección 2 | **Adaptado:** una DenseNet no se guarda como Pipeline de sklearn, así que se guardan los parámetros de la transformación |
| H2 | `rx-predecir` sobre imágenes nuevas | Consigna p. 4; S06 p. 31; S09 p. 20 (predecir sobre datos nuevos) | **Conforme** |
| H3 | 46 pruebas automáticas | Consigna p. 5 y p. 8 (pytest como eje del camino individual); nb 10/01_regresion_simple c. 53-55 (comparar el modelo cargado con el original) | **Adaptado:** unittest en lugar de pytest |

## 9. Estadísticas recalculadas con las medidas de clase

S04 p. 47 indica qué medida de asociación usar según el tipo de variables, y pp. 37 y 39 cómo leerla. El notebook 00 decidió mirando porcentajes y medias; con estas medidas, las decisiones se sostienen.

| Variables | Medida | Valor | Lectura (S04) | Respalda |
|---|---|---|---|---|
| Vista AP × Effusion (112.120 imágenes) | Phi | 0,079 (χ² = 702) | Despreciable, aunque significativa | No excluir AP por la prevalencia |
| Vista AP × 10 o más estudios previos | Phi | 0,284 | Débil, cerca de moderada | Excluir AP por ser otra población |
| Edad × Effusion (train) | Punto biserial | 0,145 | Débil | No balancear por edad |
| Sexo × Effusion (train) | Phi | 0,005 (p = 0,60) | Despreciable | No balancear por sexo |
| Estudios previos × Effusion (train) | Punto biserial; Spearman (S03 p. 50) | 0,245; 0,321 | Moderada | Riesgo de atajo |

Índices de desbalance de S05 p. 7. Con dos clases, el máximo de la entropía de Shannon es 1 y el de Gini, 0,5:

| Proporción de positivas | Entropía de Shannon | Gini |
|---|---|---|
| 9,8% (todas las PA) | 0,462 | 0,177 |
| 15,8% (test oficial, PA) | 0,630 | 0,266 |
| 40% (los tres conjuntos) | 0,971 | 0,480 |

Las imágenes de un mismo paciente no son independientes, y la independencia es un supuesto del χ² (S04 p. 21): los p-valores son optimistas, pero las magnitudes no cambian.

## 10. Medias, varianzas y umbrales verificados

- **Media y desvío:** recalculados sobre todos los píxeles de train. A: 0,507690 y 0,265400 (515.307.520 píxeles); B: 0,510635 y 0,263361. Coinciden con `preprocessing.json` y con `modelo.pt`. Validación (media 0,509) y test (0,476) no intervienen.
- **Varianza:** el código divide por N; S04 p. 5 define la varianza muestral con n − 1. Con cientos de millones de píxeles la diferencia es despreciable.
- **Umbral 0,414:** es el de máximo F1 en validación (0,800, contra 0,798 con 0,5). `best_threshold` solo recibe predicciones de validación, y el umbral quedó guardado en `modelo.pt` antes de evaluar test.
- **F1 y AUC:** F1 = 2VP / (2VP + FP + FN); AUC por rangos, con los empates valiendo 0,5. Las pruebas los comparan con cálculos a mano.
- **Bootstrap:** 2.000 remuestreos de pacientes, percentiles 2,5 y 97,5, semilla 42.

**Efecto del test remezclado (C5).** En el test preparado, las negativas son 65% sin hallazgos y como máximo 3 por paciente. En las negativas PA del test oficial son 51,4% sin hallazgos y sin tope. Reponderando la especificidad de B por grupo, con el recall fijo en 93,1%:

| Mezcla de negativas | Especificidad | F1 con 40% | F1 con 15,8% |
|---|---|---|---|
| Test preparado | 61,8% | 0,744 | 0,470 |
| Natural, por tipo de negativa | 58,7% | 0,730 | 0,451 |
| Natural, por tipo y estudios previos | 54,2% | 0,711 | 0,426 |

Es un análisis posterior: no cambia modelos ni umbrales.

**El atajo, medido.** Correlación de Spearman entre el puntaje de B y los estudios previos, dentro de cada clase:

| Clase | Validación | Test |
|---|---|---|
| Negativas | 0,26 | 0,49 |
| Positivas | 0,03 | −0,03 |

Entre las negativas, a más estudios previos, más puntaje; entre las positivas no hay relación. Es lo esperable si el modelo aprende en parte "paciente internado".

## 11. Correcciones hechas el 12/11

- **README:** PEAS con las seis dimensiones del entorno y el tipo de agente; cronología del Charter; F1 como ejemplo de la consigna; costo de los errores y punto de operación con recall ≥ 95%; 40% como pedido del profesor; medidas de asociación, Shannon y Gini en el EDA; justificación de z-score, interpolación, sin filtros, CNN, parámetros, hiperparámetros, validación única y test de hipótesis; "submuestra del test oficial"; atajo medido; especificidad reponderada; umbral según prevalencia; "7.252 a 22.594 imágenes"; GitHub de Martin Mousist.
- **`docs/RESULTADOS_MODELOS.md`, `docs/MODELO_C.md`, `docs/SPLITS_NIH_EFFUSION.md`, `docs/PREPARAR_DATOS.md`, `docs/ORGANIZACION.md`:** las mismas correcciones, el IC de la especificidad (59,5) y las PNG RGBA opacas.
- **Informe PDF:** "no se detectó diferencia significativa" en lugar de "empatan", learning rate con dos épocas sin mejora, submuestra del test, limitaciones nuevas y comandos `rx-*` en "Cómo reproducirlo".
- **Notebook 00:** faltantes, `describe()`, Shannon y Gini, Phi y punto biserial con α = 0,05, outliers con IQR y ±3σ, justificación de los cortes, y "pedido del profesor" en lugar de "la consigna pide".
- **GitHub Pages:** diagrama de la arquitectura y demo interactiva del umbral sobre las predicciones de validación.
- **`models/`:** se versionan los `report.json` e `historial.csv` de A, C, el control y las comparaciones.

## 12. Pendiente: depende del equipo

- **Acceso al repositorio (prioridad alta):** es privado y el docente no es colaborador. Marcos (admin) tiene que invitarlo o hacerlo público. El historial conserva `Slides/` y `git-profe/` (commit 81e9ece): consultarlo con el docente antes de hacerlo público.
- **Horas en los commits:** la consigna (pp. 10-11) evalúa que los mensajes digan el problema resuelto y las horas invertidas. Ponerlas desde ahora y, si se puede, una tabla retrospectiva por integrante en `docs/ORGANIZACION.md`.
- **Issues:** abrir issues para el roadmap y los pendientes (rúbrica, p. 12).
- **Reparto del trabajo:** qué hizo cada integrante.
- **Opcional, sin reentrenar:** intervalos de confianza por subgrupo y comparar las intensidades de train, validación y test (S06 pp. 32-34).
- **Opcional, con reentrenamiento:** búsqueda de hiperparámetros en validación y varias semillas por modelo.
