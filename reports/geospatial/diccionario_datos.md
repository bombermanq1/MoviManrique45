# Diccionario del módulo geoespacial

## Categorías aprobadas — cierre v1

Cada evento pertenece exactamente a una categoría. Las etiquetas son derivadas;
no cambian la comuna de la fuente ni las coordenadas originales.

| categoria_analisis | Filas actuales | Regla y uso |
|---|---:|---|
| principal_50m | 604 | Dentro del buffer estricto de 50 m recortado a Manrique; indicador principal |
| sensibilidad_borde | 40 | Fuera de Manrique, intersecta Aranjuez, distancia al límite <=0.01 m y al eje <=50 m; no suma al principal |
| revision_territorial | 4 | Resto de registros externos; revisión humana pendiente |
| resto_manrique | 7684 | Dentro de Manrique, fuera del corredor estricto |
| sin_posicion_validada | 0 | Reserva para registros no georreferenciables; no suma al principal |

El umbral de 1 cm identifica sensibilidad, no modifica el polígono ni amplía la
selección. La versión conserva por ID los conjuntos 604/40/4 en
[ids_cierre_v1.json](../../src/geospatial/ids_cierre_v1.json); una discrepancia
detiene la exportación y requiere revisar/versionar explícitamente la decisión.

| Campo adicional | Tipo | Definición |
|---|---|---|
| categoria_analisis | texto no nulo | Clave a categorias_analisis.csv; partición exclusiva |
| es_indicador_principal | booleano | Equivale a dentro_corredor_50m en las 8332 filas actuales |
| sensibilidad_borde | booleano | Solo los 40 casos de sensibilidad; excluidos del principal |
| pendiente_revision_territorial | booleano | Solo los cuatro externos restantes; no etiqueta los 40 como errores |
| distancia_limite_manrique_m | decimal nullable | Distancia al borde geométrico, no precisión certificada de la fuente |
| territorio_geometrico | texto nullable | Polígono donde cae el punto; independiente del num_comuna original |

Los campos espaciales nulos siguen siendo desconocidos. En filas sin posición
validada, los tres indicadores booleanos son falsos, pero la dimensión señala
que la categoría requiere revisión; no significa que su ubicación sea correcta.

`fragmentos_revision.csv` contiene seis filas y la clave `parte_id`. Relacionar
objectid con segmentos.segmento_cercano_id (segmentos 1:N fragmentos). Los campos
`decision_version=conservar_sin_eliminar_ni_fusionar` y
`origen_documentado=reproducible_por_recorte_territorial` distinguen la decisión
aprobada de `clasificacion`, que sigue requiriendo revisión funcional.

El control [crs_raw_cierre.json](crs_raw_cierre.json) compara la etiqueta
EPSG:9377 de la malla RAW con sus coordenadas geográficas. La discrepancia es
conocida y se conserva; cualquier cambio de ese estado detiene el cierre v1.

## Hechos de siniestros (CSV y capa siniestros)

| Campo | Tipo | Definición |
|---|---|---|
| evento_id | texto, único | objectid de la fuente, conservado como clave técnica |
| anio / mes_numero | entero nullable | año y mes obtenidos de fecha ISO validada |
| clase_siniestro | texto | categoría de la fuente, espacios externos recortados |
| gravedad_siniestro | texto | gravedad registrada, no conteo de víctimas |
| barrio / num_comuna | texto | clasificación territorial original |
| fecha_valida | booleano | fecha interpretable como YYYY-MM-DD |
| coordenada_valida | booleano | longitud/latitud numéricas dentro del rango mundial; no certifica posición local |
| distancia_carrera45_m | decimal nullable | distancia mínima al eje en EPSG:9377 |
| dentro_manrique | booleano nullable | punto intersecta el polígono oficial, incluido borde |
| dentro_corredor_50m | booleano nullable | intersecta buffer recortado, incluido borde |
| segmento_cercano_id | entero nullable | objectid de línea más próxima, empate por menor ID |
| zona_id | texto nullable | celda floor(x/100)_floor(y/100), solo para puntos en Manrique |
| geometry | Point | solo GeoPackage, EPSG:9377; no CSV de Power BI |

Se omiten dirección, radicado y hora exacta de los datasets consumidores.
Los campos espaciales nulos indican ausencia de análisis espacial para la fila;
no son distancias cero ni falsos. Los campos vacíos de categorías se representan
como SIN INFORMACION. El CSV conserva todas las filas; la capa espacial solo
contiene las que pasan el control de coordenadas y entorno local.

## Eje y auditoría

| Capa/campo | Definición |
|---|---|
| referencia | atributos y geometría original de las 26 entidades |
| segmentos.objectid | clave vial única; segmento_cercano_id en CSV |
| segmentos.longitud_m | longitud calculada de la geometría actual, no atributo histórico longitud |
| segmentos.valida / duplicada | geometría válida/no vacía; duplicación tras normalizar WKB |
| partes.parte_id | objectid:ordinal de parte en la fuente; estable mientras no cambie la geometría |
| partes.parte | ordinal 1-based de parte, sin alterar el original |
| partes.longitud_m / diminuta | longitud en metros; diminuta si <1 m |
| partes.clasificacion | posible conexión válida / posible error geométrico / revisión manual |
| extremos.extremo_id / lado | parte_id:lado, 0 inicio y 1 final |
| extremos.vecino_parte / distancia_vecino_m | parte ajena más cercana y distancia extremo-a-línea |
| extremos.conexiones_*m | cantidad de otras partes a la tolerancia indicada, incluye mismo objectid |
| discontinuidades | líneas analíticas extremo-vecino para revisar, no trazados viales propuestos |
| relaciones_partes.csv | pares cercanos, distancia, tipo de intersección, longitud de solape y cruce |

Las conexiones toleradas no prueban intersección a nivel: faltan elevación y
restricciones de circulación. No se eliminaron ni fusionaron fragmentos.

## Concentraciones y zonas

| Campo | Definición |
|---|---|
| zona_id | clave fija por índices de cuadrícula del CRS |
| cantidad | registros georreferenciados dentro de Manrique en la celda |
| heridos / muertos | conteos de categorías HERIDOS y MUERTOS, no personas |
| cerca_100m | registros de la celda a <=100 m de Carrera 45 |
| prioritaria | conteo >= P90 de celdas ocupadas y cerca_100m>0 |
| geometry | celda recortada al límite oficial, EPSG:9377 en GPKG |

Las celdas de borde tienen áreas distintas y no se calculan tasas por área.
El criterio depende del tamaño/origen de la cuadrícula y del período disponible.
Los resúmenes por dimensión tienen columna `cantidad`: número de filas, incluidos
nulos en su propio grupo. Los campos de identidad no son medidas sumables.

## Web

Carrera: objectid, longitud_m. Fragmentos: parte_id, objectid, longitud_m,
clasificacion. Celdas: zona_id, cantidad, prioritaria. Geometría EPSG:4326,
coordenadas en orden longitud, latitud. No incluye identificadores de eventos.
