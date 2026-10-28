# Análisis espacial de los siniestros

> Evidencia de una ejecución anterior del cierre geoespacial. Se conservan
> sus resultados y tablas; no equivale a una nueva comprobación de PostgreSQL
> ni a las pruebas del frontend. Para el funcionamiento actual, consulta la
> [arquitectura](arquitectura.md).


El indicador principal conserva los 604 casos del corredor estricto. Los 40
casos sensibles al borde y los cuatro externos restantes se muestran aparte.
El umbral de 0.01 m permite reconocer esa sensibilidad; no cambia la geometría
del corredor.

```text
  categoria_analisis  cantidad
       principal_50m       604
      resto_manrique      7684
revision_territorial         4
  sensibilidad_borde        40
```
```text
                     indicador      valor
                     registros       8332
         coordenadas_invalidas          0
              fechas_invalidas          0
              anio_discrepante          0
               duplicados_fila          0
           radicados_repetidos          0
coincidencias_fecha_coordenada         65
                     raw_total     235820
       ids_comuna_reproducidos       True
           fuera_entorno_local          0
         fuera_limite_manrique         44
                  corredor_50m        604
               corredor_previo        604
               ids_solo_actual          0
               ids_solo_previo          0
                     fecha_min 2019-01-01
                     fecha_max 2025-12-31
               celdas_ocupadas        439
              umbral_prioridad       43.2
            zonas_prioritarias         12
```

## Sensibilidad a la distancia

```text
 distancia_m  proximidad  proximidad_en_manrique
          30         593                     553
          50         644                     604
          75         871                     831
         100         982                     942
```

## Registros por año

```text
 anio  cantidad
 2019      1524
 2020      1142
 2021      1413
 2022      1317
 2023       942
 2024       849
 2025      1145
```

## Registros por gravedad

```text
gravedad_siniestro  cantidad
             DAÑOS      1551
           HERIDOS      6781
```

## Registros por tipo de siniestro

```text
clase_siniestro  cantidad
      ATROPELLO      1513
 CAIDA OCUPANTE       536
         CHOQUE      3711
           OTRO      2046
    VOLCAMIENTO       526
```

La selección se reproduce desde el RAW mediante `num_comuna=Comuna 3`.
`objectid` es obligatorio y único. Compartir radicado, fecha o coordenadas no
basta para demostrar que dos filas sean el mismo siniestro; esas coincidencias
no se eliminan automáticamente.

Se valida fecha ISO, concordancia del año, categorias, rango mundial de coordenadas y entorno local (envolvente de Manrique ampliada 0.1 grados). Coordenadas fuera del entorno no se proyectan: permanecen en tabla de hechos con campos espaciales nulos. Coordenadas validas no garantizan exactitud del geocodificado.

Distancias EPSG:9377 a la union del eje, tolerancia numerica 0.000001 m. Corredor: buffer Shapely de 50 m recortado al limite oficial; incluye borde. La aproximacion poligonal del arco del buffer puede diferir de distancia<=50 en el limite.

Concentraciones: cuadricula fija de 100 m anclada en (0,0) del CRS, recortada a Manrique; solo celdas ocupadas. Cada punto pertenece a una celda por floor(x/tamaño), floor(y/tamaño). Prioridad exploratoria: cantidad >= percentil 90.0% de celdas ocupadas (umbral 43.19999999999999) y al menos un registro a <=100 m del eje. Empates incluidos.

No son hotspots estadisticamente significativos, causalidad, atribucion de via ni tasas de riesgo. Faltan exposicion, aforos y poblacion comparable. Variaciones anuales pueden reflejar cobertura o reporte; no equivalen a cambios del riesgo. No se presupone que 2025 sea un año completo.

Los controles de esta ejecución revisaron unicidad, selección desde RAW,
identificadores y relectura de capas con su CRS. La comprobación de PostgreSQL
se documenta en la [validación previa](validacion_final.md); las decisiones
posteriores están en el [cierre](cierre_tecnico.md).
