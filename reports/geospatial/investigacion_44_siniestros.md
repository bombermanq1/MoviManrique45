# Investigación de los 44 siniestros fuera de Manrique

Se comparan los puntos originales con el polígono oficial suministrado; no se corrigen coordenadas ni etiquetas.

```text
             comprobacion resultado
                    count        44
coordinates_identical_raw      True
    outside_also_epsg4326        44
            near_road_50m        40
       unique_coordinates        10
 largest_coordinate_group        16
     raw_hashes_unchanged      True
      near_boundary_max_m  0.001791
```

## Distancia al límite (metros)

```text
estadistico     valor
      count 44.000000
       mean  1.403558
        std  5.126436
        min  0.000003
        25%  0.000199
        50%  0.000264
        75%  0.000333
        max 26.684032
```

## Tolerancia: cuántos puntos quedan a esa distancia o menos del límite

```text
tolerancia_m  cantidad
        0.01        40
         0.1        40
           1        40
           5        41
          10        41
          25        43
          50        44
```

## Territorio geométrico y año

```text
                     territorio  cantidad
                    04:Aranjuez        40
90:Corregimiento de Santa Elena         3
                     01:Popular         1
```
```text
  anio  cantidad
2019.0         1
2022.0         3
2024.0         2
2025.0        38
```

## Los cuatro puntos no subcentimétricos

```text
 objectid           territorio_geometrico  distancia_limite_m  distancia_carrera45_m
   125795 90:Corregimiento de Santa Elena            3.730551            1849.898916
   140908 90:Corregimiento de Santa Elena           15.664917            1536.991509
   154532 90:Corregimiento de Santa Elena           15.664917            1536.991509
   192142                      01:Popular           26.684032             250.790112
```

## Interpretación y límites

Las coordenadas se contrastan por objectid contra RAW. La discrepancia nominal/geométrica ya existe en la fuente, no se originó al filtrar o exportar. La coincidencia de la clasificación en EPSG:4326 y EPSG:9377 permite descartar que dependa únicamente de la reproyección. Los conteos por tolerancia muestran cuánto puede explicarse por proximidad al borde, sin adoptar una corrección automática.

No es posible decidir solo con estos datos si el origen es precisión de geocodificación, asignación administrativa, eje de vía limítrofe o cambios históricos del límite. No se cuenta con precisión posicional certificada ni versiones anuales del polígono. Estar cerca del límite no demuestra error. La repetición de coordenadas tampoco demuestra eventos duplicados.

La diferencia entre 644 puntos próximos al eje y 604 del corredor se explica por los 40 registros fuera de Manrique a <=50 m. Los otros cuatro puntos externos no están dentro de esa distancia. Se conservan los 44 registros en hechos, con dentro_manrique=false y zona_id nulo.

Los 40 puntos del borde están como máximo a 1.791060217027754 mm. La precisión numérica de los cálculos no equivale a precisión posicional de la fuente. El conteo estricto de 604 debe presentarse junto con esta sensibilidad: tolerar 1 cm en el límite incorporaría esos 40 registros próximos sin cambiar su posición. No se adoptó esa tolerancia ni se cambió la selección.

Detalle por objectid, sin dirección ni radicado: [CSV de revisión](../../data/processed/geospatial/siniestros_fuera_manrique_revision.csv). El contraste con PostgreSQL se registra en [validación final](validacion_final.md).
