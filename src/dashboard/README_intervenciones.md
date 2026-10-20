# Módulo de zonas identificadas y posibles soluciones

## Propósito

El módulo **Posibles soluciones en la Carrera 45** permite consultar las 12
zonas identificadas por MoviManrique45. Presenta los registros históricos de
cada celda y un catálogo de opciones para orientar una revisión técnica
posterior.

No ejecuta, aprueba ni presupone una intervención física. Todas las fichas
inician en el estado **Pendiente de inspección**.

## Arquitectura

`src/dashboard/intervenciones.py` lee exclusivamente:

- La tabla validada de hechos mediante `cargar_hechos()`.
- `data/processed/geospatial/web/zonas_prioritarias.geojson`.
- `data/processed/geospatial/web/carrera45.geojson`.

Antes de exportar, valida el cierre de 8.332 eventos y los IDs congelados de
las categorías principal, borde y revisión. Después genera
`web/data/intervenciones.json`; esta es una vista derivada y local para el
dashboard. No modifica fuentes RAW, datasets procesados, geometrías, IDs ni
PostgreSQL.

`src/dashboard/exportar_web.py` actualiza conjuntamente el payload existente
del dashboard y el payload de intervenciones. El cliente estático consume ambos
archivos y enlaza la selección de ficha con el resaltado de la zona en el
geovisor SVG.

## Datos que muestra cada ficha

- Identificador real de zona, centroide de referencia y bounds en EPSG:4326.
- Registros históricos de la celda, periodo, categorías territoriales,
  gravedad, tipo y barrios nominales observados.
- `objectid` de los segmentos del eje que intersectan geométricamente la
  celda, cuando existen.
- Orden descriptivo por número de registros históricos. No es una puntuación
  de riesgo ni una prioridad oficial.
- Qué revisar en campo, catálogo de ocho opciones, justificación, estado y nota
  de costo pendiente.

Los conteos se asocian por el `zona_id` de la grilla ya utilizada en los
productos geoespaciales. La intersección de una celda con el eje aporta
contexto espacial; no atribuye un siniestro a la Carrera 45.

## Posibles soluciones y costo

El catálogo incluye pasos peatonales seguros, reductores y control de
velocidad, señalización, accesibilidad universal, rampas y cruces, protección
de peatones en contextos de transporte, y visibilidad o espacio peatonal.
Cada ficha presenta estas medidas como opciones sujetas a inspección, diseño,
autorización y evaluación de la entidad competente.

El costo por zona se mantiene como **Pendiente de estudio técnico y
presupuesto**. 


de accesibilidad. Por ello, el módulo no estima riesgo, causalidad, efectividad
ni prioridad institucional de una obra.
