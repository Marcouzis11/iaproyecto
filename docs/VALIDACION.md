# Estado de validación del flujo de preparación

El flujo de preparación y su versión en notebooks están implementados. La ejecución sobre radiografías reales está pendiente de descargar y seleccionar el dataset.

## Comprobado con datos sintéticos

- Instalación en el entorno virtual del repositorio y dependencias compatibles.
- Ejecución completa de ambos notebooks con un kernel nuevo.
- Las 12 pruebas del pipeline pasaron también usando el código de las celdas del notebook.
- La demo de 120 imágenes artificiales generó 84 imágenes de train, 18 de validación y 18 de test.
- Se comprobaron independencia por paciente, duplicados, exclusiones, uint16, conservación de las particiones oficiales de prueba y estadísticas calculadas solo con train.
- Se comprobó la carga de los arrays finales y la visualización de imágenes originales y procesadas.

Estos resultados verifican el código con ejemplos controlados, no su funcionamiento sobre una descarga real ni el rendimiento de un modelo.

## Próxima comprobación: dataset real

1. Descargar imágenes y metadatos de una de las fuentes indicadas en `datasets/`.
2. Elegir el hallazgo y ajustar las rutas del notebook 01.
3. Ejecutar todo sobre una muestra con soporte suficiente de ambas clases por paciente.
4. Revisar las exclusiones, las proporciones de las particiones y las imágenes procesadas.
5. Confirmar que los CSV y arrays se corresponden y documentar si la descarga fue parcial.
6. Conservar la configuración y los informes antes de comenzar el entrenamiento.
