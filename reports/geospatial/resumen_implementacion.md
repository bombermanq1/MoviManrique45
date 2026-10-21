# Resultado de implementación geoespacial

> El [cierre técnico v1](cierre_tecnico.md) documenta las categorías aprobadas,
> datasets actualizados y pruebas repetidas. Las decisiones actuales prevalecen
> sobre las recomendaciones y pendientes históricos de este documento.

> Este documento conserva el estado al terminar la implementación inicial.
> La [validación final posterior](validacion_final.md) resuelve la autenticación,
> confirma las coincidencias con PostGIS y QGIS, e investiga los 44 puntos externos.
> Prevalece ese informe sobre los pendientes de autenticación señalados abajo.

## Fase 1 — Entorno y fuentes: parcial por autenticación SQL

- Implementado: inspección de dependencias, inventario de fuentes, esquemas,
  conteos, geometrías, CRS y hashes; conexión SQL forzada a solo lectura.
- Archivos: [validación](../validacion_entorno_geoespacial.md),
  [inventario](environment.json), [script](../../src/geospatial/probe.py).
- Resultados: Python y librerías operativos; 235820 registros RAW, 8332 de Comuna 3,
  26 segmentos definitivos; GeoPackage externo localizado y comparado.
- Pruebas: importaciones, lectura de todas las fuentes y conexión con timeout.
- Problema: PostgreSQL pide contraseña no disponible para libpq.




## Fase 2 — Siniestros: análisis local ejecutado

- Implementado: filtro desde RAW, fechas, coordenadas, duplicados, distancias,
  sensibilidad, agregación temporal/categórica, cuadrícula y prioridades descriptivas.
- Archivos: [GPKG](../../data/processed/geospatial/siniestros_analisis.gpkg),
  [reporte](../analisis_espacial_siniestros.md), sensibilidad_distancias.csv.
- Resultados: 8332 filas, sin IDs/radicados repetidos ni fechas/coordenadas fuera
  de rango; 65 registros comparten fecha/coordenadas sin prueba de duplicación.
  44 puntos quedan fuera del polígono oficial. 644 a <=50 m, 604 dentro del
  corredor recortado; los 604 IDs coinciden exactamente con el resultado previo.
  439 celdas ocupadas de 100 m; 12 prioritarias según frecuencia y proximidad.
- Pruebas: conservación de filas y claves, conteos por agrupación, IDs previos,
  validez espacial, distancias máximas y límites.
- Problemas: ubicación nominal y geométrica difieren en 44 registros; se conservan.
- Pendiente: verificación SQL y evaluación experta de exactitud/cobertura.
  No se calculan tasas de riesgo ni significación de hotspots.

## Fase 3 — Automatización: ejecutada y reproducida

- Implementado: [módulos](../../src/geospatial/), configuración, validaciones,
  staging de GPKG, reemplazo de productos, hashes y logging de errores.
- Archivos: código, [configuración](../../src/geospatial/config.json),
  [manifiesto](run.json), log local y [pruebas](../../tests/test_geospatial.py).
- Resultados: ejecuciones repetidas conservan todas las filas y hashes lógicos.
  SHA-256 de RAW, archivos procesados anteriores y GPKG de revisión sin cambios.
- Pruebas: geometrías sintéticas, límites de cuadrícula, CRS faltante,
  transformación, coordenadas inválidas y bloqueo de escritura fuera de derivados.
- Problemas resueltos: conflicto de nombre `run` en unittest; promoción automática
  LineString→MultiLineString del escritor, desactivada y comprobada por WKB.
- Pendiente: no hay transacción conjunta de todos los archivos. Tras un fallo,
  revisar log y pruebas antes de consumir productos. No se programaron tareas recurrentes.

## Fase 4 — QGIS: generado y validado

- Implementado: proyecto local con 10 capas, nombres/leyenda, colores diferenciados,
  concentraciones graduadas, CRS 9377 y rutas relativas; capas de solo lectura.
- Archivos: [proyecto](../../qgis/MoviManrique45_Analisis.qgz),
  [guía](../../qgis/README.md), [validación](qgis_validation.json),
  [render](qgis_preview.png).
- Resultados: QGIS 3.44.15 reabre todas las capas; render sin errores, inspeccionado.
- Pruebas: proveedores válidos, CRS, conteos y reapertura real del QGZ.
- Problema resuelto: cierre inicial de PyQGIS devolvió código no cero después
  de escribir productos; se liberaron proveedores antes de cerrar QGIS y la
  ejecución posterior finalizó con código cero.
- Pendiente: revisión humana de fragmentos y conexiones; no requiere conexión SQL.

## Fase 5 — Power BI: datasets preparados y validados

- Implementado: hechos de 8332 registros, dimensiones de 26 segmentos y 439
  zonas, resúmenes por año, gravedad, clase, barrio y corredor.
- Archivos: [datasets y guía](../../powerbi/geospatial/README.md),
  [diccionario](diccionario_datos.md).
- Resultados: claves únicas, relaciones verificadas, sumas de resúmenes coherentes.
- Pruebas: integridad referencial y conteos contra capas; nulos territoriales conservados.
- Problemas: dimensión de zona contiene agregados estáticos; se documenta usar
  conteo de hechos para filtros interactivos y evitar duplicar medidas.
- Pendiente: importar en Power BI cuando corresponda. No se modificaron dashboards.

## Fase 6 — Web: capas preparadas y validadas

- Implementado: EPSG:4326 y lista explícita de atributos; celdas con mínimo 5
  registros, sin puntos individuales, direcciones, radicados ni IDs de eventos.
- Archivos: [GeoJSON](../../data/processed/geospatial/web/),
  [integración](integracion_web.md).
- Resultados: 26 segmentos, seis fragmentos, 342 celdas exportables, 12 prioridades.
- Pruebas: JSON parseable, CRS 4326, rangos geográficos locales, geometrías válidas
  y ausencia de campos personales innecesarios.
- Problemas: no se redondean fragmentos de centímetros; tamaños ya son pequeños.
- Pendiente: integración futura, sin construir ni publicar frontend/backend.

