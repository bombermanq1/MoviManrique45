# Construcción manual de las cuatro páginas

Esta guía usa exclusivamente las tablas, medidas y GeoJSON validados del
repositorio. No presupone que Azure Maps, referencias GeoJSON o la publicación
en línea estén habilitados. Construya primero las páginas con visuales nativos y
agregue capas de referencia solo después de probarlas en el equipo local.

## Preparación común

1. Termine la carga de Power Query y confirme `ControlCierreEstricto` sin error.
2. Cree las relaciones de [modelo_relaciones.md](modelo_relaciones.md).
3. Cree las medidas de [dax/medidas_modelo.dax](dax/medidas_modelo.dax).
4. Cree una navegación inferior con botones o navegadores de página:
   `Resumen general`, `Carrera 45`, `Análisis geográfico` y
   `Calidad y trazabilidad`.
5. Sincronice los segmentadores `DimFecha[Año]` y
   `DimTerritorioNominal[barrio]` solo en las páginas 1–3. La página 4 debe
   conservar controles de trazabilidad visibles sin que los filtros oculten el
   cierre completo.
6. Use títulos dinámicos o texto visible cuando una tarjeta responda a filtros.
   No etiquete una cifra filtrada como “total Comuna 3”.

La paleta recomendada es: principal `#007C83`, sensibilidad de borde `#B86E00`,
revisión territorial `#9C3D58`, resto `#66758C` y prioridad exploratoria
`#6D4C91`. Los colores representan categorías analíticas, no gravedad ni riesgo.

## Página 1 — Resumen general

**Pregunta:** ¿Cómo se distribuyen los registros disponibles de Comuna 3?

1. Inserte segmentadores de año y barrio en la parte superior.
2. Agregue tarjetas con `[Registros]`, `[Registros corredor]` y
   `[Porcentaje corredor sobre Comuna 3]`. Rotule las dos primeras como
   “registros en selección” cuando existan filtros.
3. Inserte un gráfico de columnas: eje `DimFecha[Año]`, valor `[Registros]`.
4. Inserte barras horizontales por `DimGravedad[gravedad_siniestro]` y
   `DimTipo[clase_siniestro]`, ambas con `[Registros]`.
5. Agregue una matriz de `DimFecha[Año]` por
   `DimClasificacion[categoria_analisis]` con `[Registros]`.
6. En **Editar interacciones**, haga que barras y matriz filtren los demás
   visuales; no configure filtros de página al corredor principal.

**Aceptación sin filtros:** 8.332 registros, 604 principal, 7,25 % y la matriz
suma 8.332. La gravedad debe mostrar 6.781 HERIDOS y 1.551 DAÑOS.

## Página 2 — Carrera 45

**Pregunta:** ¿Qué se observa descriptivamente en el corredor estricto?

1. Reuse los filtros sincronizados de año y barrio.
2. Inserte tarjetas: `[Registros corredor]`,
   `[Porcentaje corredor sobre Comuna 3]` y `[Mediana distancia corredor m]`.
3. Cree un gráfico combinado o dos gráficos alineados por `DimFecha[Año]` con
   `[Registros]` y `[Registros corredor]`; no use un doble eje.
4. Añada barras de gravedad y tipo con una interacción/filtro visual de
   `DimClasificacion[categoria_analisis] = principal_50m`, o bien use la medida
   `[Registros corredor]` en los valores.
5. Agregue una nota permanente: “40 casos sensibles al borde están excluidos
   del indicador principal. La proximidad espacial no implica causalidad.”

**Aceptación sin filtros:** 604; por año 2019–2025: 86, 45, 36, 115, 111, 95,
116. Por gravedad: 534 HERIDOS y 70 DAÑOS. No presentar estos valores como
tasas o cambios de riesgo.

## Página 3 — Análisis geográfico

**Pregunta:** ¿Dónde están los registros y las zonas exploratorias del cierre?

1. Cree una vista base con el visual **Mapa** o **Azure Maps** usando
   `FactSiniestros[latitud]`, `FactSiniestros[longitud]`,
   `DimClasificacion[categoria_analisis]` y `[Registros]`.
2. Configure el tooltip con `evento_id`, `anio`, gravedad, clase,
   `distancia_carrera45_m`, categoría y `zona_id_modelo`. No agregue dirección,
   radicado ni otros datos innecesarios.
3. Agregue a un lateral una tabla de zonas: `DimZona[zona_id]`,
   `[Registros]`, `DimZona[prioritaria]`; permita filtrar por prioridad.
4. Incluya `SIN_ZONA` en la tabla para conservar los 44 registros externos.
5. Como contexto, use los GeoJSON existentes en
   `data/processed/geospatial/web/`: `carrera45.geojson` (26 líneas),
   `zonas_prioritarias.geojson` (12 polígonos) y
   `fragmentos_revision.geojson` (6 partes). Agréguelos únicamente si el visual
   local permite referencias GeoJSON y la prueba de correspondencia se aprueba.
6. Si el visual no admite referencias, conserve el mapa de puntos y use el
   proyecto QGIS como referencia técnica. No simule una capa geográfica no
   verificada.

**Aceptación:** el mapa de puntos responde a año/barrio/categoría; las zonas
prioritarias se mantienen como clasificación fija de versión, no se recalculan
con filtros. El GeoJSON de concentraciones contiene 342 geometrías publicables,
no las 439 celdas analíticas completas; no lo rotule como cobertura total.

## Página 4 — Calidad y trazabilidad

**Pregunta:** ¿Qué decisiones y límites sostienen el indicador?

1. Agregue tarjetas con `[Registros sensibilidad borde]`,
   `[Registros revisión territorial]`, `[Fragmentos conservados de la versión]`,
   `[Conteo IDs congelados principal]` y `[Integridad IDs principal]`.
2. Use una tabla de `RevisionFragmentos` con `parte_id`, `objectid`, `longitud_m`,
   `origen_documentado` y `decision_version`.
3. Cree una tabla de eventos filtrada a `sensibilidad_borde` y
   `revision_territorial` que solo muestre `evento_id`, territorio geométrico,
   distancia al límite y categoría. No muestre direcciones ni radicados.
4. Incluya texto visible de método: 604 es el corredor territorial estricto;
   40 son sensibilidad al borde; las geometrías se procesaron sin rellenar gaps;
   la malla RAW tiene una advertencia CRS documentada.
5. Añada limitaciones: rango válido de coordenadas no demuestra precisión,
   cercanía no implica causalidad y no se calculan tasas de riesgo.

**Aceptación sin filtros:** 40 sensibilidad, 4 revisión, 6 fragmentos, 604 IDs
con integridad `OK`. La información fija del cierre no debe desaparecer por un
filtro temporal de eventos.

## Prueba final en Desktop

Antes de guardar, pruebe: sin filtros; año 2025 (1.145 totales, 116 principal);
gravedad HERIDOS (6.781 totales, 534 principal); tipo ATROPELLO (1.513 totales,
172 principal); y selección de sensibilidad (40 registros y cero inflados en la
tarjeta principal). Guarde, cierre, reabra y actualice. Solo tras estas pruebas
se puede declarar un PBIX/PBIP funcional.
