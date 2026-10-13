# Abrir el análisis en QGIS

Abrir [MoviManrique45_Analisis.qgz](MoviManrique45_Analisis.qgz) con QGIS.
Conservar la estructura relativa `qgis/` y `data/processed/geospatial/`:
el proyecto referencia los dos GeoPackage derivados, sin conexión a PostgreSQL.

Incluye límite, concentraciones graduadas por cantidad, prioridad exploratoria,
corredor, referencia original, siniestros, auditoría, discontinuidades, fragmentos
y extremos. La leyenda está en el panel de capas con nombres explícitos.
Los candidatos de discontinuidad y los extremos están inicialmente ocultos para
evitar saturar el mapa. Activarlos para la inspección; ampliar a la capa de
fragmentos para observar geometrías de pocos centímetros. El color rojo resalta
fragmentos; su pequeño tamaño impide distinguirlos a escala de toda la comuna.

Todas las capas se configuran como solo lectura en QGIS. CRS EPSG:9377.
Las capas referencia y revisión coinciden espacialmente; alternar visibilidad
para compararlas. No editar ni guardar cambios sobre los archivos originales.

Generación, reapertura y render probados con QGIS 3.44.15-Solothurn.
Evidencia: [qgis_validation.json](../reports/geospatial/qgis_validation.json) y
[vista previa](../reports/geospatial/qgis_preview.png). La vista fue inspeccionada
visualmente; esto no sustituye la revisión técnica de cada fragmento.

Regenerar con el comando documentado en el [módulo](../src/geospatial/README.md).
Cerrar el proyecto antes de regenerar sus GeoPackage para evitar bloqueos de Windows.
