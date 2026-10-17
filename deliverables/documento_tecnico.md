# Documento técnico MoviManrique45

## Problema y objetivo

MoviManrique45 organiza datos históricos de siniestros viales para apoyar la revisión técnica de seguridad vial en el entorno de Carrera 45 y Comuna 3 - Manrique, Medellín. El objetivo es mostrar patrones descriptivos, trazables y reproducibles sin afirmar causalidad o riesgo.

## Fuentes y metodología

Se emplean registros de siniestros de la Alcaldía de Medellín, malla vial oficial y límite territorial de comunas. La malla vial declara EPSG:9377 pero sus coordenadas almacenadas son geográficas; el procesamiento conserva el RAW y corrige la interpretación solo en memoria antes de transformar a EPSG:9377. El eje definitivo conserva 26 segmentos y 1.698,67 m dentro de Manrique. El corredor analítico usa 50 m y se recorta al límite oficial.

## Resultados

El universo nominal contiene 8.332 siniestros entre 2019 y 2025. El indicador principal reúne 604 eventos en el corredor territorial estricto. Otros 40 casos próximos al borde se clasifican como sensibilidad y cuatro quedan en revisión territorial. La proximidad simple de 50 m produce 644 eventos y no sustituye el indicador estricto. El cierre conserva seis fragmentos menores de un metro y 12 zonas prioritarias exploratorias dentro de 439 celdas de concentración.

## Arquitectura y prototipo

Los scripts Python reproducen ingesta, ETL y validación. Los derivados geoespaciales alimentan QGIS, archivos de Power BI y el dashboard web local. El dashboard verifica los conteos y los IDs congelados antes de exportar una vista navegable con filtros, gráficos y geovisor. Power BI cuenta con diseño, M, DAX y relaciones preparadas, pero no se validó en Desktop.

## Componente exploratorio y limitaciones

Las concentraciones son un análisis espacial descriptivo. No existe modelo predictivo porque faltan variables de exposición y validación prospectiva. Los registros históricos no estiman riesgo ni prueban causalidad. Las recomendaciones requieren evaluación de campo, diseño y aprobación por autoridades competentes.

## Recomendaciones preliminares

Las zonas exploratorias pueden orientar revisiones de cruces, señalización, velocidad, accesibilidad universal y operación de motocicletas y transporte público. No representan obras aprobadas.
