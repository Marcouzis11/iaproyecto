# Plan de trabajo: clasificación de hallazgos en radiografías de tórax

> **Documento histórico.** Es el plan del 21 de octubre de 2026, antes de elegir el dataset y entrenar. Lo que se hizo y los resultados están en el [README](../README.md). Los slides y la consigna que cita son material de la cátedra y no están en este repositorio.

**Base conceptual:** los PDF de `Slides/`. **Base de datos:** las fuentes enlazadas en `datasets/` y los archivos que se obtengan de ellas.

**Revisión:** 21 de octubre de 2026. **Estado:** planificación; no hay un modelo entrenado ni resultados medidos en este repositorio.

Este plan aplica los conceptos de la cursada al problema de tórax. No utiliza `consigna.pdf`, `git-profe/`, rúbricas externas ni el plan anterior como fundamento. No sustituye la comprobación posterior de los requisitos de entrega de la materia.

Las referencias a páginas cuentan desde la primera página del PDF. Se distinguen tres niveles:

- **Slides:** contenido explicado o presentado en las láminas.
- **Aplicación al proyecto:** decisiones propuestas al adaptar esos conceptos a radiografías; no son instrucciones textuales del docente.
- **Pendiente:** información que debe comprobarse en los datos o conocimiento de implementación que los slides no desarrollan.

## 1. Qué queremos construir

Un programa que reciba una radiografía de tórax y estime la presencia de hallazgos definidos en el dataset. La pregunta es: **¿el modelo puede reconocer las etiquetas elegidas en imágenes de pacientes que no utilizó para aprender?**

Se trata de aprendizaje supervisado: las imágenes son las entradas `X` y las anotaciones del dataset son las salidas `y`. Como se predicen categorías, corresponde clasificación. Base: slides 01, p. 31 y p. 47; slides 09, pp. 16–23.

### Alcance progresivo propuesto

1. **Primera versión binaria:** elegir un hallazgo disponible y distinguir etiqueta positiva de negativa para ese hallazgo. Elegirlo después de contar ejemplos y revisar la calidad de sus anotaciones.
2. **Ampliación:** estimar varios hallazgos por imagen, si los datos y los resultados de la primera versión lo permiten. Si pueden coexistir, la tarea es multietiqueta; no hay que obligar a elegir una sola patología. Esta adaptación y su implementación no están desarrolladas en los slides.

Una etiqueta negativa para un hallazgo no significa que la radiografía sea normal. El objetivo es reproducir anotaciones del dataset en un prototipo académico; no confirmar un diagnóstico ni afirmar que alguien está sano.

No se fijan de antemano cinco patologías, una red concreta ni una cifra de rendimiento. Se decidirán con evidencia de los datos y validación.

## 2. Qué material sirve y cómo se aplica

| Material local | Concepto útil | Aplicación al proyecto |
|---|---|---|
| 01 — Fundamentos IA/ML, pp. 31, 47, 65–98 | Supervisado, modelos de clasificación y herramientas | Definir imagen/etiqueta; preparar Python y considerar KNN, SVM o árboles |
| 02 — Introducción al análisis, pp. 14–15 | Problema → datos → EDA → preparación → entrenamiento | Orden general del trabajo; ejemplo de un sistema visual |
| 03 — EDA, pp. 19–23, 53–64 | Resúmenes numéricos, frecuencias, gráficos y contingencias | Describir imágenes, etiquetas, desbalance y coexistencia de hallazgos |
| 04 — Faltantes, pp. 48–57 | Outliers y causas de faltantes | Diferenciar errores, casos raros, etiquetas ausentes e incertidumbre |
| 05 — Limpieza, pp. 6–14, 17–24, 37–38 | Desbalance, particiones, limpieza y codificación | Preparar metadatos y la variable objetivo |
| 06 — Nuevas features, pp. 5, 8–12, 19–31, 51 | Fuga, features, escalado, balance y preparación de imágenes | Construir un pipeline que aprenda transformaciones solo de train |
| 08 — Optimización, pp. 24–26 | Gradiente y tasa de aprendizaje | Explicar el ajuste si el modelo elegido utiliza optimización por gradiente |
| 09 — Aprendizaje automático, pp. 16–23, 24–47 | Generalización, sesgo/varianza, validación e hiperparámetros | Comparar candidatos y separar selección de evaluación final |
| EXTRA — Computer Vision I, pp. 24–29, 34–42, 44–75 | Matrices, canales, lectura, grises, umbralización y filtros | Inspeccionar las radiografías y experimentar con su representación |

No es necesario utilizar todos los temas. Agentes, BFS, A*, Hanoi y algoritmos genéticos no resuelven una necesidad inicial de este clasificador. El slide 10 desarrolla regresión: sus errores MAE/MSE/RMSE no se trasladan automáticamente a esta clasificación. La regularización ya tiene una base general en el slide 09, p. 47.

## 3. Etapa 1: obtener y entender los datos

En el clon revisado solo se encontraron estos enlaces dentro de `datasets/`; no se encontraron imágenes ni tablas de etiquetas allí:

| Archivo local | Fuente enlazada | Estado de la revisión |
|---|---|---|
| `datasets/dataset1/link` | [NIH ChestX-ray](https://nihcc.app.box.com/v/ChestXray-NIHCC) | El enlace de Box no pudo inspeccionarse con la herramienta; contenido y esquema pendientes |
| `datasets/dataset2/link` | [CheXpert](https://stanfordmlgroup.github.io/competitions/chexpert/) | Se consultó la descripción oficial del dataset; no se descargaron los datos |

La única consulta web utilizada para fundamentar este plan fue a las fuentes que ya enlaza `datasets/`, para entender los datos. No se tomaron arquitecturas ni recetas de entrenamiento de Internet.

La descripción oficial de CheXpert distingue etiquetas positivas, negativas, inciertas y no mencionadas: `1`, `0`, `-1` y vacío, respectivamente. Una imagen puede asociarse a distintas observaciones. Esto obliga a revisar las etiquetas antes de construir el target; no se debe convertir automáticamente todo vacío o incierto en negativo. Fuente: [CheXpert, extracción de etiquetas](https://stanfordmlgroup.github.io/competitions/chexpert/).

### Tareas

- [ ] Comprobar acceso y condiciones de uso de las dos fuentes.
- [ ] Elegir **una** para la primera versión según accesibilidad, documentación, etiquetas y recursos disponibles. No mezclar ambas inicialmente.
- [ ] Obtener el diccionario de datos, metadatos y una muestra pequeña de imágenes.
- [ ] Registrar versión, origen, archivos obtenidos y si la descarga es parcial.
- [ ] Vincular cada imagen con sus etiquetas e identificador de paciente, si está disponible.
- [ ] Revisar vistas y formatos; propuesta inicial: trabajar con una vista homogénea, preferentemente frontal si los metadatos permiten identificarla.
- [ ] Elegir el hallazgo inicial con positivos y negativos suficientes para formar los conjuntos de trabajo.

**Entregable:** ficha del dataset y tabla imagen–etiqueta–paciente. **Cierre:** poder abrir una imagen y explicar de dónde sale su etiqueta.

## 4. Etapa 2: auditoría, limpieza y particiones

Base: slides 04, pp. 48–57; 05, pp. 8–24; 06, p. 5; 09, pp. 38–46.

- [ ] Detectar filas repetidas, rutas inexistentes, imágenes ilegibles y etiquetas inválidas.
- [ ] Distinguir archivos ausentes por descarga parcial de imágenes realmente dañadas.
- [ ] Registrar exclusiones y su motivo. Una radiografía poco habitual no es automáticamente un error eliminable.
- [ ] Mantener incierto y no mencionado diferenciados. Para el primer experimento binario con CheXpert, se propone utilizar solo positivos y negativos explícitos del hallazgo elegido; informar cuántos se excluyen y cómo limita la muestra. Es una decisión de alcance, no una regla de los slides.
- [ ] Separar entrenamiento, validación y prueba antes de ajustar transformaciones o modelos. Respetar particiones oficiales cuando sean aplicables.
- [ ] Como adaptación para evitar fuga, mantener todas las imágenes de un paciente en un solo conjunto y evitar duplicados entre conjuntos. Esta regla por paciente no aparece como receta específica en los slides: aplica su principio de independencia al problema.
- [ ] Comprobar representación de positivos y negativos en cada conjunto. La estratificación se busca sin romper la separación por paciente.
- [ ] Guardar asignaciones y semilla. Propuesta si hay que construir tres conjuntos propios: aproximadamente 70/15/15 por pacientes, sujeta a soporte por clase; no es una proporción impuesta por las láminas.

Si no puede verificarse independencia por paciente, documentar la limitación y resolverla antes de presentar una evaluación como independiente.

**Entregable:** tabla limpia, registro de exclusiones y particiones. **Cierre:** conjuntos trazables con clases evaluables y sin pacientes compartidos.

## 5. Etapa 3: EDA de desarrollo

Base: slides 03, pp. 19–23 y 53–64; 05, pp. 6–7; 06, p. 51; EXTRA, pp. 24–29.

Realizar el análisis para decisiones de modelado sobre train. Usar validación para comparar alternativas; reservar test para el final. Los conteos mínimos necesarios para verificar la integridad de las particiones no implican estudiar los errores de test.

- [ ] Contar imágenes y pacientes; obtener frecuencias absolutas y relativas de etiquetas.
- [ ] Graficar positivos, negativos, inciertos y no mencionados por separado cuando existan.
- [ ] Describir dimensiones, canales, tipo numérico y rango de intensidad real de los archivos. No asumir que todo tiene rango 0–255 por el ejemplo de uint8 del EXTRA.
- [ ] Mostrar imágenes de distintas etiquetas e histogramas de píxeles; revisar orientación, contraste y calidad.
- [ ] Si hay edad, sexo o vista, describir sus distribuciones y faltantes como contexto. No utilizarlos automáticamente como entradas.
- [ ] Para la ampliación, usar tablas de contingencia y gráficos de coexistencia de etiquetas.
- [ ] Registrar preguntas que afecten el pipeline: tamaños distintos, desbalance, ruido, anotaciones incompletas y posibles señales ajenas al hallazgo.

**Entregable:** notebook de EDA con conclusiones que justifiquen decisiones. **Cierre:** explicar qué problemas de los datos se tratarán y por qué.

## 6. Etapa 4: preparar las imágenes y construir las entradas

Base: slides 02, p. 15; 06, pp. 8–12, 19–31 y 51; EXTRA, pp. 24–29 y 34–75.

- [ ] Leer y visualizar imágenes con OpenCV; verificar si ya están en grises.
- [ ] Adoptar dimensiones comunes. Elegir una resolución experimental que permita ejecutar una prueba corta, comprobando visualmente qué detalle se pierde. El ejemplo industrial de los slides no fija la resolución óptima de tórax.
- [ ] Definir escalado de intensidades acorde al formato. Si se calculan medias, desviaciones, mínimos o máximos del conjunto, obtenerlos solo con train y reutilizarlos.
- [ ] Mantener el mismo procesamiento determinista al validar, probar y predecir una imagen nueva.
- [ ] Preparar una representación numérica para un clasificador sencillo. Propuesta inicial: imagen reducida en grises convertida a vector; alternativa experimental: resúmenes de intensidad e histogramas. Son aplicaciones de representación matricial, estadística y feature engineering, no descriptores diagnósticos enseñados en los slides.
- [ ] Codificar el target binario como positivo/negativo y guardar la correspondencia.

La umbralización convierte intensidades en una imagen binaria; **no convierte por sí sola una radiografía en un diagnóstico**. No aplicarla como paso obligatorio. Si se prueba, comparar contra grises y revisar pérdida de detalle. Tampoco aplicar filtros gaussianos o de mediana solo por estar en el temario: incorporarlos si un experimento de validación los justifica.

**Entregable:** transformación reproducible imagen → entrada numérica. **Cierre:** transformar una muestra sin errores y poder mostrar original y resultado.

## 7. Etapa 5: entrenar una primera versión sencilla

Base: slide 01, p. 47, que presenta KNN, SVM y árboles de decisión para clasificación; slide 06, pp. 19–21; slide 09, pp. 16–39.

### Experimentos propuestos

| Experimento | Qué permite comprobar | Qué se ajusta o conserva |
|---|---|---|
| Referencia trivial | Qué ocurre al predecir siempre la clase mayoritaria de train | Clase mayoritaria; propuesta de comparación |
| KNN sobre entradas visuales preparadas | Si esa representación permite separar las etiquetas por proximidad | Ejemplos de train y elección de `k` en validación |
| Árbol de decisión, si hace falta comparar | Si otro modelo presentado en clase mejora la referencia | Complejidad del árbol seleccionada en validación |

KNN es un primer candidato, no una promesa de buen rendimiento. Su ajuste conserva los ejemplos de entrenamiento; no aprende una red mediante gradiente. El tamaño de los vectores y la cantidad de imágenes pueden volverlo costoso: medir memoria y tiempo con una muestra antes de ampliar. SVM queda como alternativa si hay una razón concreta para probarlo.

- [ ] Preparar un entorno Python con NumPy, pandas, OpenCV, visualización y scikit-learn, herramientas presentadas en los slides.
- [ ] Ejecutar primero un ensayo pequeño de carga, transformación, ajuste y predicción.
- [ ] Comparar pocas configuraciones sobre la misma partición de validación.
- [ ] Si el desbalance perjudica la clase minoritaria, comparar un tratamiento presentado en el slide 06, p. 26, aplicado solo a train; no balancear validación ni test.
- [ ] Registrar representación, parámetros, semilla, tamaño de muestra, tiempo y resultados.
- [ ] Comparar errores de train y validación para detectar sobreajuste o subajuste, según el slide 09, pp. 24–36.

Los slides nombran estos clasificadores y scikit-learn, pero no contienen una implementación completa de este pipeline. Al programarlo hará falta completar el uso de la API con documentación de la herramienta; eso es un faltante de implementación, no una razón para imponer una arquitectura externa.

**Entregable:** primer clasificador ajustado y tabla de experimentos. **Cierre:** predecir en validación y explicar qué aprendió o conservó el modelo y cómo se eligió su configuración.

## 8. Etapa 6: seleccionar y evaluar el modelo final

Base: slide 05, p. 7, matriz de confusión; slide 09, pp. 19, 38–47.

- [ ] Comparar la matriz de confusión de validación con la referencia trivial y contar aciertos, falsos positivos y falsos negativos. No aceptar como evidencia suficiente un alto porcentaje de aciertos que provenga de ignorar la clase minoritaria.
- [ ] Acordar antes de evaluar test cómo se compararán errores y aciertos de ambas clases. Los slides aportan la matriz, pero no desarrollan aquí un protocolo completo de métricas de clasificación: completar ese criterio es un pendiente técnico.
- [ ] Si se necesitan precision, recall o F1 para comparar candidatos, documentar sus definiciones con material complementario antes de usarlos. No atribuir su desarrollo a estos PDF ni copiar automáticamente métricas de regresión.
- [ ] Usar validación para elegir modelo y configuración. Considerar validación cruzada solo si el costo lo permite y manteniendo pacientes separados; el slide 09, p. 46, admite validación única en procesos costosos.
- [ ] Congelar la configuración seleccionada y el procedimiento de ajuste. Si se decide reajustar con train y validación unidos, hacerlo una vez con esa configuración, sin incorporar test; volver a calcular allí las transformaciones aprendidas y guardar el artefacto resultante.
- [ ] Evaluar una vez el artefacto final en test, comparándolo con la referencia trivial sobre los mismos casos.
- [ ] Informar tamaño de cada clase, errores, tiempo de predicción y limitaciones. No fijar ahora una cifra de rendimiento sin datos.
- [ ] Analizar casos acertados y fallidos. Si se cambia el modelo a partir de test, declarar su reutilización y reservar otra evaluación independiente para la nueva versión.

**Entregable:** evaluación final con resultados reales. **Cierre:** explicar qué logra el modelo en datos reservados, frente a qué referencia y con qué limitaciones.

## 9. Etapa 7: guardar y usar el modelo

Aplicación práctica del flujo entrenamiento → evaluación → predicción del slide 09, p. 20. La persistencia del artefacto requiere completar detalles de implementación.

- [ ] Guardar el clasificador, su preprocesamiento, el mapa de etiquetas y la configuración juntos o con referencias inequívocas.
- [ ] Crear una función o comando que reciba una imagen, aplique el mismo pipeline y devuelva la etiqueta estimada.
- [ ] Comprobar que cargar el modelo en otra ejecución reproduce la predicción sin entrenar de nuevo.
- [ ] Documentar cómo obtener datos, instalar dependencias, entrenar, evaluar y predecir.
- [ ] Preparar una demostración con casos reservados e indicar qué hallazgo evalúa.

La primera entrega puede ser un notebook reproducible y un predictor sencillo. Una web, API o publicación no es necesaria para resolver esta etapa y no se impone en este plan.

**Entregable:** artefacto reutilizable, instrucciones y demo. **Cierre:** usar una imagen nueva sin repetir el entrenamiento.

## 10. ¿Alcanza lo de los slides para conseguir el modelo final?

**Alcanza para fundamentar el proceso y plantear un prototipo sencillo; no contiene todos los detalles para implementarlo, ni garantiza que clasifique bien radiografías.**

| Necesidad | Qué aportan las fuentes actuales | Qué falta resolver |
|---|---|---|
| Definir clasificación supervisada | Slides 01 y 09 | Elegir etiquetas a partir de los datos reales |
| Explorar, limpiar, dividir y preparar imágenes | Slides 02–06 y EXTRA | Descargar archivos, verificar esquema y ejecutar el pipeline |
| Probar un clasificador sencillo | Modelos nombrados en 01, p. 47; validación en 09 | Uso concreto de la API, representación y medición empírica |
| Manejar anotaciones inciertas | Descripción de CheXpert y conceptos de faltantes | Política explícita y análisis de los casos que se excluyen |
| Medir clasificación | Matriz de confusión y generalización | Completar el criterio de selección y métricas necesarias |
| Entrenar una CNN para radiografías | Menciones de redes y librerías, no una receta completa | Arquitectura, capas, pérdida, entrenamiento y recursos |
| Usar transferencia de aprendizaje | No se desarrolla un procedimiento en los PDF revisados | Pesos de origen, adaptación y ajuste si se elige ese camino |
| Predecir varios hallazgos simultáneos | Las etiquetas del dataset motivan la tarea | Codificación multietiqueta, modelo compatible y evaluación por hallazgo |
| Descargar un modelo final ya entrenado | Los enlaces del repo son de datasets | Identificar y verificar un artefacto compatible; no se asume que esté incluido |

En el EXTRA, la tabla de contenidos de p. 2 menciona regresión logística, pero el cuerpo del PDF desarrolla representación y procesamiento de imágenes. No debe considerarse una clase completa de regresión logística por ese índice. Del mismo modo, los filtros por convolución explicados allí no constituyen una explicación de una red convolucional entrenable.

### Si el primer modelo no alcanza

1. Verificar etiquetas, errores del pipeline, independencia de particiones y representación.
2. Comparar alternativas sencillas de las presentadas en clase, usando validación.
3. Si la representación sigue siendo insuficiente, justificar la ampliación a aprendizaje de características con una red y completar únicamente el material que falta. No elegir ResNet, pesos preentrenados, pérdida o hiperparámetros como si vinieran de los slides.
4. Volver a recorrer entrenamiento, selección y evaluación con el nuevo enfoque. El test anterior no sirve para elegirlo y luego presentarlo como independiente.

La ampliación requiere material complementario o explicación docente. No se incorpora una receta de Internet en esta revisión. También puede aceptarse como resultado académico un modelo limitado, siempre que se evalúe y se expliquen sus fallos; eso debe contrastarse por separado con las condiciones de entrega de la materia.

## 11. Orden de ejecución y evidencia mínima

| Orden | Resultado verificable | Depende de |
|---|---|---|
| 1 | Dataset elegido, muestra accesible y hallazgo inicial definido | Acceso y diccionario |
| 2 | Auditoría y particiones independientes | Imágenes, etiquetas y pacientes |
| 3 | EDA y decisiones justificadas | Train reservado |
| 4 | Preprocesamiento y representación reproducibles | Formatos y recursos comprobados |
| 5 | Referencia trivial y primer clasificador | Pipeline y criterio de comparación |
| 6 | Selección por validación y evaluación final | Experimentos documentados |
| 7 | Modelo guardado y predicción desde otra ejecución | Artefacto final y configuración |
| 8 | Ampliación a más hallazgos o red, si se justifica | Resultados y material faltante resuelto |

Primer paso concreto: conseguir metadatos y una muestra de una de las fuentes enlazadas. Mientras eso no ocurra, siguen pendientes el hallazgo elegido, los tamaños efectivos, las particiones definitivas y la viabilidad del entrenamiento. No hay resultados que completar con números supuestos.
