# Fase 3 — Analisis espacial de siniestros

Cierre v1 aprobado: 604 IDs estrictos como indicador principal; 40 en sensibilidad al borde sin sumarlos al principal; cuatro externos en revision territorial. Categorias mutuamente excluyentes. El umbral de 0.01 m identifica sensibilidad, no ensancha el corredor.

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

## Distribucion por anio

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

## Distribucion por gravedad_siniestro

```text
gravedad_siniestro  cantidad
             DAÑOS      1551
           HERIDOS      6781
```

## Distribucion por clase_siniestro

```text
clase_siniestro  cantidad
      ATROPELLO      1513
 CAIDA OCUPANTE       536
         CHOQUE      3711
           OTRO      2046
    VOLCAMIENTO       526
```

Filtro reproducido desde RAW por num_comuna=Comuna 3. No se eliminan duplicados por radicado o por fecha/coordenada: no bastan para demostrar un mismo evento. objectid es obligatorio y unico.

Se valida fecha ISO, concordancia del año, categorias, rango mundial de coordenadas y entorno local (envolvente de Manrique ampliada 0.1 grados). Coordenadas fuera del entorno no se proyectan: permanecen en tabla de hechos con campos espaciales nulos. Coordenadas validas no garantizan exactitud del geocodificado.

Distancias EPSG:9377 a la union del eje, tolerancia numerica 0.000001 m. Corredor: buffer Shapely de 50 m recortado al limite oficial; incluye borde. La aproximacion poligonal del arco del buffer puede diferir de distancia<=50 en el limite.

Concentraciones: cuadricula fija de 100 m anclada en (0,0) del CRS, recortada a Manrique; solo celdas ocupadas. Cada punto pertenece a una celda por floor(x/tamaño), floor(y/tamaño). Prioridad exploratoria: cantidad >= percentil 90.0% de celdas ocupadas (umbral 43.19999999999999) y al menos un registro a <=100 m del eje. Empates incluidos.

No son hotspots estadisticamente significativos, causalidad, atribucion de via ni tasas de riesgo. Faltan exposicion, aforos y poblacion comparable. Variaciones anuales pueden reflejar cobertura o reporte; no equivalen a cambios del riesgo. No se presupone que 2025 sea un año completo.

Pruebas de fase: unicidad, filtro RAW, IDs congelados del cierre, relectura de capas/CRS. PostgreSQL fue contrastado en la validacion final previa; este cierre no reabre la base. Ver [validacion SQL](geospatial/validacion_final.md) y [cierre](geospatial/cierre_tecnico.md).
