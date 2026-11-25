# Mejoras para el final

Después de la devolución del MVP, cada integrante toma una mejora y la trabaja en su fork. Las tres parten del mismo código (tag `base-final`), usan los mismos datos preparados y siguen el mismo protocolo, así que los resultados se comparan entre sí y contra el modelo B sin dudas sobre qué cambió.

## Quién hace qué

| Integrante | Mejora | Rama | Punto de la devolución |
|---|---|---|---|
| Tiziano Bertorello | Llegar a F1 0,80 | `mejora/f1-080` | 1: el objetivo no se alcanza |
| Marcos Agustín García Mombello | Otra arquitectura: EfficientNet-B0 | `mejora/efficientnet-b0` | En el MVP no se probó otra red |
| Martin Mousist | Modelo B con 3 semillas | `mejora/semillas-b` | 2: variación entre entrenamientos |

### Llegar a F1 0,80 (Tiziano)

Con AUC ~0,90 ningún umbral pasa de 0,80 (se vio con el modelo C): hace falta un modelo que separe mejor las clases, no otro umbral. Variantes posibles:

- Pesos preentrenados en radiografías, por ejemplo los de torchxrayvision entrenados con CheXpert o MIMIC. Nunca pesos entrenados con NIH: ya vieron las imágenes de nuestro test.
- Resolución mayor que 224×224, donde los derrames chicos no se pierdan. Requiere preparar de nuevo desde NIH con otro `image_size` y la misma semilla, y publicar la lista de esa preparación con `rx-verificar-datos --generar`. Como las imágenes y los pacientes son los mismos, `rx-comparar` compara contra B con las predicciones guardadas.
- Negativas difíciles o un ensamble de modelos.

Cada variante se elige en validación y se informan todas las que se probaron, no solo la mejor. El 0,80 se busca en validación y se confirma en test una sola vez, con el modelo elegido.

### EfficientNet-B0 (Marcos)

La misma receta que B cambiando solo la red, para que la diferencia se deba a la arquitectura:

- `src/rx_torax/training/model.py`: agregar `efficientnet_b0` en `build_model`, con los pesos de ImageNet de torchvision y la última capa (`classifier[1]`) reemplazada por una salida.
- `configs/modelo_b_efficientnet_b0.json`: copia de `configs/modelo_b.json` con `architecture` y `output` cambiados. Si hace falta otro learning rate, se elige en validación y se informa.
- `rx-predecir` y `rx-evaluar` funcionan sin cambios. El mapa de calor de `rx-probar` (`puntaje_y_mapa` en `src/rx_torax/inference/app.py`) repite el `forward` de DenseNet121 y hay que adaptarlo: EfficientNet no aplica ReLU después de `features`.

### Modelo B con 3 semillas (Martin)

- `configs/modelo_b_semilla1.json` y `configs/modelo_b_semilla2.json`: copias de `configs/modelo_b.json` con `seed` y `output` cambiados. La semilla de los datos queda en 42: cambian la inicialización, el orden de los lotes y el aumento de datos.
- Cada semilla elige su época y su umbral en validación y se evalúa una vez en test.
- Resultado: media y desvío del F1, la AUC y el umbral entre las semillas 42, 1 y 2, comparados con el ancho del intervalo bootstrap (0,035 en el F1 de test).
- B se entrenó en una Mac M4 (MPS). Si las semillas nuevas se entrenan en Colab, conviene entrenar también la 42 ahí, para que las tres compartan hardware. En MPS ni la misma semilla da pesos idénticos.

## La base común

1. **Código:** el tag `base-final` de `main`. Todas las ramas `mejora/*` salen de ahí.
2. **Datos:** la carpeta `data/processed/nih_effusion_pa_modelo_b_v1` (5,8 GB, 14 archivos), la misma que produjo los resultados de B. Se comparte por Google Drive y, antes de entrenar, se verifica:

   ```bash
   rx-verificar-datos data/processed/nih_effusion_pa_modelo_b_v1
   ```

   Tiene que decir "14 archivos idénticos". Compara cada archivo con el SHA-256 de `configs/nih_effusion_pa_modelo_b_v1.sha256`. Sin esto, una diferencia en los datos se confundiría con el efecto de la mejora.
3. **Referencia:** el modelo B (semilla 42). Validación: F1 0,800, AUC 0,905, umbral 0,414. Test: F1 0,744 (0,726 a 0,761), AUC 0,869. Sus predicciones por imagen están en `models/modelo_b_densenet121_v1/evaluacion_*/`.
4. **Entorno:** las versiones fijadas de `pyproject.toml`, instaladas con `python -m pip install -e .`.

## Protocolo

- Train ajusta los pesos; validación elige la época, el umbral y la variante; test se evalúa una sola vez por modelo final. `rx-evaluar` no deja evaluar dos veces el mismo conjunto.
- Cada experimento va a una carpeta nueva de `models/`; `rx-entrenar` se niega a pisar una existente.
- La comparación con B es pareada por paciente, con α = 0,05, primero en validación y, después de la evaluación única, en test:

  ```bash
  rx-evaluar --modelo models/<nuevo> --conjunto val
  rx-comparar --modelos models/modelo_b_densenet121_v1 models/<nuevo> --nombres B <Nuevo> --conjunto val --salida models/comparacion_val_b_<nuevo>
  rx-evaluar --modelo models/<nuevo> --conjunto test
  rx-comparar --modelos models/modelo_b_densenet121_v1 models/<nuevo> --nombres B <Nuevo> --conjunto test --salida models/comparacion_test_b_<nuevo>
  ```

- Se versionan la configuración, `report.json`, `historial.csv`, los `report.json` y `predicciones_*.csv` de cada evaluación y los `report.json` de las comparaciones; `.gitignore` ya los deja pasar. Los pesos del modelo final de cada mejora se versionan como los de A, B, control y C, agregando su ruta a las excepciones de `.gitignore`; los de variantes descartadas quedan en Drive.
- Antes del pull request, `rx-recalcular` tiene que decir que todos los resultados coinciden. La integración continua lo vuelve a correr.
- Cada mejora se documenta en su propio archivo (`docs/MEJORA_F1_080.md`, `docs/MEJORA_EFFICIENTNET_B0.md`, `docs/MEJORA_SEMILLAS_B.md`). El README y los documentos compartidos no se tocan en los forks, para no generar conflictos: los tres resultados entran al README en un último pull request.

## Forks y ramas

Tiziano y Martin hacen un fork de `Marcouzis11/iaproyecto` desde GitHub (botón *Fork*). Marcos es el dueño del repositorio y GitHub no deja hacer un fork del propio, así que trabaja en la rama `mejora/efficientnet-b0` del original, con las mismas reglas.

```bash
git clone https://github.com/<usuario>/iaproyecto.git
cd iaproyecto
git remote add upstream https://github.com/Marcouzis11/iaproyecto.git
git fetch upstream --tags
git switch -c mejora/<nombre> base-final
```

Si `main` cambia, se trae con `git fetch upstream` y `git merge upstream/main`. Los commits siguen la convención de [organización](ORGANIZACION.md), con fecha real. Al terminar, cada uno abre un pull request de su rama `mejora/*` contra `main` del original, que se integra con la integración continua en verde.

## Entrenar en Google Colab

Para quien no tenga una Mac con MPS o una GPU. Con la carpeta `nih_effusion_pa_modelo_b_v1` subida a Drive y un entorno de ejecución con GPU (*Entorno de ejecución > Cambiar tipo*):

```python
from google.colab import drive
drive.mount('/content/drive')
```

```bash
!git clone -b mejora/<nombre> https://github.com/<usuario>/iaproyecto.git
%cd iaproyecto
!pip install -q -e .
!mkdir -p data/processed && cp -r /content/drive/MyDrive/<carpeta>/nih_effusion_pa_modelo_b_v1 data/processed/
!rx-verificar-datos data/processed/nih_effusion_pa_modelo_b_v1
!rx-entrenar --config configs/<config>.json
!rx-evaluar --modelo models/<salida> --conjunto val
!cp -r models/<salida> /content/drive/MyDrive/<carpeta>/
```

El último paso guarda el modelo en Drive: Colab borra todo al cerrar la sesión, y si se corta durante el entrenamiento la corrida se pierde. B tardó 79 minutos en una Mac M4; en Colab depende de la GPU asignada.
