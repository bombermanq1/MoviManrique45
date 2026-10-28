# Datos y metodología

Esta guía explica de dónde salen los registros y cómo se define el corredor.
Para identificar un campo del CSV o del JSON, consulta el
[diccionario de datos](diccionario_datos.md).

## Fuentes

Los scripts de ingesta consultan servicios ArcGIS REST de la Alcaldía de
Medellín:

- [Siniestros viales](https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Accidentes/MapServer/0).
- [Malla vial](https://www.medellin.gov.co/servidormapas/rest/services/vivienda_ciudad_terri/VM_Base_overview/MapServer/1).
- [Límite catastral de comunas y corregimientos](https://www.medellin.gov.co/servidormapas/rest/services/ServiciosCatastro/Base_Catastral/MapServer/0).

Las descargas se conservan localmente en `data/raw/`. Los datos procesados, el
eje y las capas para la web están en `data/processed/`. El archivo
`powerbi/geospatial/hechos_siniestros.csv` también es un insumo del dashboard,
aunque esté en la carpeta de Power BI.

Los insumos locales no versionados necesarios para regenerar la vista web se
detallan en [manifest_demo_v1.json](../data/manifest_demo_v1.json), con tamaño
y hash de cada archivo. No se incluyen automáticamente en un clon del
repositorio. El script `scripts/verificar_insumos_demo.py` comprueba su
integridad sin modificarlos.

## Qué significan las cifras

La fuente asigna **8.332 registros** a Comuna 3. Al comprobar sus coordenadas
contra el límite oficial, 44 quedan fuera. Se conservan todos y se clasifican
en cuatro grupos que no se superponen:

| Categoría | Registros | Interpretación |
| --- | ---: | --- |
| Corredor estricto | 604 | Dentro del corredor de 50 m recortado al límite oficial de Manrique. |
| Sensibilidad al borde | 40 | Casos externos próximos al borde que se registran por separado y no se suman al indicador principal. |
| Revisión territorial | 4 | Casos externos restantes, pendientes de revisión. |
| Resto de Manrique | 7.684 | Registros fuera del corredor estricto que no pertenecen a las categorías anteriores. |

Los **644** casos del análisis anterior de proximidad a 50 m son una
comparación metodológica; no reemplazan los **604** del corredor estricto.
El eje vial definitivo tiene **26 segmentos** dentro del polígono de Manrique.
Las listas de identificadores de cierre están en
[ids_cierre_v1.json](../src/geospatial/ids_cierre_v1.json): los controles
comprueban los IDs, no solo las cantidades.

Las **12 zonas exploratorias** provienen de una cuadrícula de 100 m recortada
a Manrique. Se seleccionan las celdas ocupadas cuyo conteo alcanza el percentil
90 y que tienen al menos un registro a 100 m o menos del eje. Una zona puede
incluir siniestros fuera del corredor estricto. Su ficha utiliza el historial
completo de la celda, aunque el usuario filtre el dashboard.

La selección ayuda a organizar la revisión en campo. No asigna prioridad
oficial ni prueba que una intervención concreta sea necesaria.

## Coordenadas y límites de interpretación

Las distancias se calculan en EPSG:9377, en metros; las capas de la web se
presentan en EPSG:4326. La malla vial RAW declara EPSG:9377, pero sus
coordenadas almacenadas son geográficas. Esa discrepancia conocida se conserva
en el archivo original y requiere tratar el CRS correctamente en memoria antes
de reproyectar. El control histórico está en
[crs_raw_cierre.json](../reports/geospatial/crs_raw_cierre.json).

La franja de 50 m es un criterio analítico del proyecto, no una norma vial. Los
conteos no incorporan aforos ni otras medidas de exposición; por tanto, no son
tasas de riesgo, predicciones ni prueba de causalidad. Las zonas tampoco
sustituyen una inspección o una decisión de la autoridad competente.

La vista `web/data/dashboard.json` contiene coordenadas de eventos individuales.
Antes de publicarla, revise las condiciones de uso de la fuente y qué nivel de
detalle es apropiado compartir.
