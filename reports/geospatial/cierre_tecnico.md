# Cierre técnico — MoviManrique45, versión cierre_v1

Las cinco decisiones indicadas por el usuario quedan implementadas en el proceso, reportes, diccionario y datasets de Power BI. El cierre conserva el criterio espacial y los 604 IDs previamente contrastados con PostGIS.

## Indicadores definitivos de esta versión

```text
  categoria_analisis  registros
       principal_50m        604
      resto_manrique       7684
revision_territorial          4
  sensibilidad_borde         40
```
Total: **8332** registros de Comuna 3. Indicador principal: **604**, equivalentes al **7.25%** del total nominal. Los 40 de sensibilidad y cuatro externos pendientes no se suman al principal. No se presentan tasas de riesgo. El conjunto por proximidad (644) se conserva únicamente como comparación metodológica.

## Decisiones implementadas

1. Corredor principal: mismo buffer de 50 m recortado a Manrique, mismo predicado y mismos 604 IDs. Una lista de referencia de la versión detiene el proceso si cambian los IDs, incluso si el conteo permanece igual.
2. Sensibilidad: los 40 puntos externos de Aranjuez a <=0.01 m del límite y <=50 m del eje reciben categoria_analisis=sensibilidad_borde. La tolerancia solo clasifica: no modifica el límite, coordenadas ni indicador.
3. Cuatro externos restantes: categoria_analisis=revision_territorial y pendiente_revision_territorial=true. Se conserva su ubicación nominal de origen y se añade territorio_geometrico separado.
4. Seis fragmentos: conservados, sin eliminar ni fusionar. El CSV de revisión registra la decisión y su origen reproducible mediante recorte territorial; no acredita conectividad funcional.
5. CRS RAW: en cada ejecución se contrasta etiqueta EPSG:9377 y bounds geográficos. Se conserva la discrepancia conocida, sin corregir el RAW. Un estado diferente detiene esta versión para revisión.

Categorías mutuamente excluyentes; resto_manrique contiene 7684 registros. sin_posicion_validada se reserva para casos sin georreferenciación válida (cero actualmente). [Diccionario](diccionario_datos.md) y [guía Power BI](../../powerbi/geospatial/README.md).

## Verificaciones ejecutadas

Pruebas: **30 aprobadas**, 0 fallos, 0 errores. Se incluyen los 22 controles previos y ocho controles de cierre: partición, IDs exactos, rechazo de sustitución de ID con igual conteo, borde sin ampliación, relaciones/agregados, fragmentos intactos, discrepancia CRS y repetición de exportaciones.

Dos ejecuciones sucesivas con las mismas fuentes, configuración y código: reproducible=True. Se compararon hashes lógicos de geometrías/tablas y bytes de 16 CSV/GeoJSON. Fuentes originales intactas: True; verificación SHA-256 incluida en pruebas. No se exige igualdad binaria de los GeoPackage por sus metadatos internos.

QGIS existente reabierto tras actualizar capas derivadas: 10 capas válidas, proyecto sin cambios=True. La comprobación SQL utiliza la evidencia previamente autenticada de solo lectura; en este cierre no se abrió una nueva conexión ni se modificaron tablas.

Evidencia: [pruebas](final_tests.txt), [manifiesto](run.json), [CRS](crs_raw_cierre.json), [QGIS](qgis_final.json).

## Archivos creados o modificados en este cierre

Lista comparada por SHA-256 con el inventario anterior al cierre. Incluye derivados regenerados; los RAW no fueron reescritos.

- actualizado: [data/processed/geospatial/carrera45_auditoria.gpkg](../../data/processed/geospatial/carrera45_auditoria.gpkg)
- actualizado: [data/processed/geospatial/siniestros_analisis.gpkg](../../data/processed/geospatial/siniestros_analisis.gpkg)
- creado: [powerbi/geospatial/categorias_analisis.csv](../../powerbi/geospatial/categorias_analisis.csv)
- creado: [powerbi/geospatial/fragmentos_revision.csv](../../powerbi/geospatial/fragmentos_revision.csv)
- actualizado: [powerbi/geospatial/hechos_siniestros.csv](../../powerbi/geospatial/hechos_siniestros.csv)
- actualizado: [powerbi/geospatial/README.md](../../powerbi/geospatial/README.md)
- creado: [powerbi/geospatial/resumen_anio_categoria.csv](../../powerbi/geospatial/resumen_anio_categoria.csv)
- creado: [powerbi/geospatial/resumen_categoria_analisis.csv](../../powerbi/geospatial/resumen_categoria_analisis.csv)
- actualizado: [reports/analisis_espacial_siniestros.md](../../reports/analisis_espacial_siniestros.md)
- actualizado: [reports/auditoria_geometrica_carrera45.md](../../reports/auditoria_geometrica_carrera45.md)
- creado: [reports/geospatial/cierre_archivos.json](../../reports/geospatial/cierre_archivos.json)
- creado: [reports/geospatial/cierre_archivos_antes.json](../../reports/geospatial/cierre_archivos_antes.json)
- creado: [reports/geospatial/cierre_ejecucion_1.log](../../reports/geospatial/cierre_ejecucion_1.log)
- creado: [reports/geospatial/cierre_ejecucion_2.log](../../reports/geospatial/cierre_ejecucion_2.log)
- creado: [reports/geospatial/cierre_tecnico.md](../../reports/geospatial/cierre_tecnico.md)
- creado: [reports/geospatial/crs_raw_cierre.json](../../reports/geospatial/crs_raw_cierre.json)
- actualizado: [reports/geospatial/diccionario_datos.md](../../reports/geospatial/diccionario_datos.md)
- actualizado: [reports/geospatial/final_tests.json](../../reports/geospatial/final_tests.json)
- actualizado: [reports/geospatial/final_tests.txt](../../reports/geospatial/final_tests.txt)
- actualizado: [reports/geospatial/pipeline.log](../../reports/geospatial/pipeline.log)
- actualizado: [reports/geospatial/resumen_implementacion.md](../../reports/geospatial/resumen_implementacion.md)
- actualizado: [reports/geospatial/run.json](../../reports/geospatial/run.json)
- actualizado: [reports/geospatial/validacion_final.md](../../reports/geospatial/validacion_final.md)
- creado: [src/geospatial/closure_policy.py](../../src/geospatial/closure_policy.py)
- creado: [src/geospatial/closure_report.py](../../src/geospatial/closure_report.py)
- actualizado: [src/geospatial/config.json](../../src/geospatial/config.json)
- actualizado: [src/geospatial/exports.py](../../src/geospatial/exports.py)
- actualizado: [src/geospatial/final_report.py](../../src/geospatial/final_report.py)
- actualizado: [src/geospatial/geometry.py](../../src/geospatial/geometry.py)
- creado: [src/geospatial/ids_cierre_v1.json](../../src/geospatial/ids_cierre_v1.json)
- actualizado: [src/geospatial/incidents.py](../../src/geospatial/incidents.py)
- actualizado: [src/geospatial/pipeline.py](../../src/geospatial/pipeline.py)
- actualizado: [src/geospatial/README.md](../../src/geospatial/README.md)
- creado: [tests/test_closure.py](../../tests/test_closure.py)

