# Datasets geoespaciales para Power BI

## Cierre v1: indicador principal y categorías separadas

El indicador principal conserva los **604 IDs** del corredor estricto. Los **40**
casos de sensibilidad al borde y los **cuatro** en revisión territorial se muestran
por separado; no se suman al principal. Los restantes **7684** están dentro de
Manrique y fuera del corredor. Total: **8332** registros, sin duplicar filas.

Agregar relación 1:N de `categorias_analisis.categoria_analisis` a
`hechos_siniestros.categoria_analisis`, con filtro unidireccional. Usar las etiquetas
de esa dimensión para segmentadores; la categoría sin posición validada tiene
cero filas actualmente. `resumen_categoria_analisis.csv` y
`resumen_anio_categoria.csv` son controles agregados, no hechos adicionales para sumar.

```dax
Indicador principal 50 m = CALCULATE(COUNTROWS(hechos_siniestros), hechos_siniestros[es_indicador_principal] = TRUE())
Sensibilidad al borde = CALCULATE(COUNTROWS(hechos_siniestros), hechos_siniestros[sensibilidad_borde] = TRUE())
Pendientes territoriales = CALCULATE(COUNTROWS(hechos_siniestros), hechos_siniestros[pendiente_revision_territorial] = TRUE())
```

Estas medidas respetan filtros de año, gravedad y categoría. Una categoría
incompatible puede dejar la medida en blanco; usar COALESCE(medida,0) si el diseño
requiere mostrar cero. No presentar 604+40 como indicador principal.

`fragmentos_revision.csv` permite una tabla de revisión con seis partes conservadas,
sus longitudes y la decisión aprobada. No duplicar la longitud del segmento al
relacionarlo con varias partes. Las categorías y geometrías no se corrigen en Power BI.

Importar CSV UTF-8 delimitados por coma. Configurar el punto como separador
decimal. No se modificaron dashboards. Cada fila de `hechos_siniestros.csv`
representa un registro fuente de Comuna 3; no una víctima ni un vehículo.

## Relaciones

| Tabla del lado 1 | Clave | Tabla del lado muchos | Clave |
|---|---|---|---|
| segmentos | segmento_cercano_id | hechos_siniestros | segmento_cercano_id |
| zonas | zona_id | hechos_siniestros | zona_id |

Usar filtro unidireccional de dimensión a hechos. `evento_id` y `zona_id` como
texto; segmento como entero; año y mes como enteros; distancia como decimal.
Convertir True/False de los CSV a tipo lógico. Celdas en blanco representan nulos,
no falso. Los 44 eventos fuera del límite oficial tienen `zona_id` nulo: conservarlos.

El segmento más cercano es una relación de proximidad, incluso a gran distancia;
no atribuye el siniestro al segmento. Para el corredor filtrar
`dentro_corredor_50m=true`. En empates se elige el menor ID vial de forma estable.
No sumar `longitud_m` después de unir segmentos con hechos: la relación 1:N la repetiría.

Los CSV `resumen_*` son comprobaciones y tablas independientes, no otra tabla de
hechos para unir o sumar a la primera. Todos sus conteos suman 8332 en esta versión.
La dimensión zonas contiene agregados de todo el período. Para respuestas a
filtros de año/gravedad, contar hechos relacionados; no sumar `zonas.cantidad`,
que es un atributo estático y no se recalcula con filtros.

## Medidas sugeridas (crear en Power BI)

```dax
Registros = COUNTROWS(hechos_siniestros)
Registros corredor = CALCULATE([Registros], hechos_siniestros[dentro_corredor_50m] = TRUE())
Porcentaje corredor = DIVIDE([Registros corredor], [Registros])
```

El denominador incluye todos los registros fuente de Comuna 3 en el contexto de
filtro, incluso los que caen fuera del polígono. Indicadores por año, gravedad,
tipo y barrio se obtienen agrupando la misma tabla. `HERIDOS` es una categoría
del siniestro; su cantidad no es el número de personas heridas.

Prioridad: celdas ocupadas de 100 m, conteo >= percentil 90 (43.2, equivalente a
44 o más registros en esta ejecución) y al menos un registro a <=100 m del eje.
No usar ese indicador como tasa de riesgo. No hay datos de exposición.

Ver [diccionario](../../reports/geospatial/diccionario_datos.md). Los datos son
derivados locales; no se realizó importación automática ni publicación a Power BI.
