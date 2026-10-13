# Capas para la futura aplicación web

Ubicación: [web](../../data/processed/geospatial/web/). Archivos GeoJSON
FeatureCollection, EPSG:4326, orden longitud/latitud. Se pueden consumir en una
biblioteca cartográfica futura; no se construyó frontend, backend ni servicio.

| Archivo | Entidades | Bytes en esta ejecución |
|---|---:|---:|
| carrera45.geojson | 26 | 7527 |
| fragmentos_revision.geojson | 6 | 1805 |
| concentraciones.geojson | 342 | 175511 |
| zonas_prioritarias.geojson | 12 | 5714 |

[manifest.json](../../data/processed/geospatial/web/manifest.json) registra el
tamaño real al regenerar. Se conserva precisión completa porque redondear podría
colapsar los fragmentos de centímetros. El tamaño total no requiere simplificar.
No usar geometrías web reproyectadas para mediciones precisas: utilizar EPSG:9377.

Concentraciones exporta solo celdas de al menos cinco registros (umbral configurable).
Se omiten eventos individuales, dirección, radicado y hora. Esta minimización no
constituye una garantía general de anonimización. No se publicaron archivos.
Las celdas omitidas implican que el total web no equivale al total de Power BI.

Mostrar leyendas como «conteo de registros» y «prioridad exploratoria»;
evitar «riesgo» o «accidentes causados por Carrera 45». Campos en el
[diccionario](diccionario_datos.md). Los fragmentos son candidatos de revisión,
no errores confirmados ni geometrías corregidas.
