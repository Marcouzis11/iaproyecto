#!/usr/bin/env bash
# Flujo completo: preparar -> entrenar -> evaluar en validación y test -> predecir.
#
#   scripts/flujo_completo.sh demo   Datos sintéticos, CPU, menos de un minuto. Prueba que el código corre; no mide la IA.
#   scripts/flujo_completo.sh nih    Reproduce el modelo B con NIH (data/raw/nih); ~1,5 h con GPU o MPS.
#
# Usa el Python del entorno virtual (.venv). Otro intérprete: PYTHON=/ruta/python scripts/flujo_completo.sh demo
set -euo pipefail

cd "$(dirname "$0")/.."
MODO="${1:-demo}"
if [ -z "${PYTHON:-}" ]; then
    if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=.venv/Scripts/python.exe; fi
fi
[ -x "$PYTHON" ] || { echo "No encuentro $PYTHON. Crear el entorno primero (ver README, Instalación)." >&2; exit 1; }

paso() { printf '\n== %s\n' "$1"; }

case "$MODO" in
    demo)
        # Salidas propias de la demo: se borran para poder repetirla.
        rm -rf data/raw/demo_sintetica data/processed/demo_sintetica_v1 models/demo_sintetica
        paso "1/5 Generar 120 imágenes sintéticas (no son radiografías)"
        "$PYTHON" -m rx_torax.demo --output data/raw/demo_sintetica
        paso "2/5 Preparar: auditoría, split por paciente y transformación"
        "$PYTHON" -m rx_torax.prepare --config configs/demo.json
        paso "3/5 Entrenar DenseNet121 sin pesos de ImageNet, 2 épocas en CPU"
        "$PYTHON" -m rx_torax.training.train --config configs/demo_modelo.json
        paso "4/5 Evaluar en validación y una sola vez en test"
        "$PYTHON" -m rx_torax.evaluation.evaluate --modelo models/demo_sintetica --conjunto val --dispositivo cpu
        "$PYTHON" -m rx_torax.evaluation.evaluate --modelo models/demo_sintetica --conjunto test --dispositivo cpu
        paso "5/5 Predecir sobre imágenes sueltas"
        "$PYTHON" -m rx_torax.inference.predict --modelo models/demo_sintetica --dispositivo cpu --json \
            data/raw/demo_sintetica/images/p000_0.png data/raw/demo_sintetica/images/p001_0.png
        printf '\nDemo terminada. Resultados en models/demo_sintetica/. Con datos al azar, AUC cerca de 0,5 es lo esperable.\n'
        ;;
    nih)
        SALIDA="${SALIDA:-models/reproduccion_modelo_b}"
        [ -f data/raw/nih/Data_Entry_2017_v2020.csv ] || {
            echo "Falta data/raw/nih/Data_Entry_2017_v2020.csv. Ver README, sección El dataset." >&2; exit 1; }
        if [ -d data/processed/nih_effusion_pa_modelo_b_v1 ]; then
            paso "1/4 Preparar: ya existe data/processed/nih_effusion_pa_modelo_b_v1, se reutiliza"
        else
            paso "1/4 Preparar NIH: solo PA, 40% de positivos en cada conjunto"
            "$PYTHON" -m rx_torax.prepare --config configs/nih_modelo_b.json
        fi
        paso "2/4 Entrenar el modelo B en $SALIDA"
        "$PYTHON" -m rx_torax.training.train --config configs/modelo_b.json --salida "$SALIDA"
        paso "3/4 Evaluar en validación y una sola vez en test"
        "$PYTHON" -m rx_torax.evaluation.evaluate --modelo "$SALIDA" --conjunto val
        "$PYTHON" -m rx_torax.evaluation.evaluate --modelo "$SALIDA" --conjunto test
        paso "4/4 Predecir sobre las radiografías de ejemplo"
        "$PYTHON" -m rx_torax.inference.predict --modelo "$SALIDA" --json examples/radiografias/*.png
        ;;
    *)
        echo "Uso: scripts/flujo_completo.sh [demo|nih]" >&2
        exit 2
        ;;
esac
