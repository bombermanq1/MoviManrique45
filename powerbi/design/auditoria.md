# Auditoría Power BI — solo lectura

No se modificaron datasets ni se ejecutó el ETL geoespacial. Tipos inferidos con pandas; los tipos semánticos para Power BI se especifican en el diseño.

| CSV | Filas | Columnas | Duplicados completos |
|---|---:|---:|---:|
| [categorias_analisis.csv](../geospatial/categorias_analisis.csv) | 5 | 4 | 0 |
| [fragmentos_revision.csv](../geospatial/fragmentos_revision.csv) | 6 | 8 | 0 |
| [hechos_siniestros.csv](../geospatial/hechos_siniestros.csv) | 8332 | 20 | 0 |
| [resumen_anio.csv](../geospatial/resumen_anio.csv) | 7 | 2 | 0 |
| [resumen_anio_categoria.csv](../geospatial/resumen_anio_categoria.csv) | 19 | 3 | 0 |
| [resumen_barrio.csv](../geospatial/resumen_barrio.csv) | 18 | 2 | 0 |
| [resumen_categoria_analisis.csv](../geospatial/resumen_categoria_analisis.csv) | 4 | 2 | 0 |
| [resumen_clase_siniestro.csv](../geospatial/resumen_clase_siniestro.csv) | 5 | 2 | 0 |
| [resumen_dentro_corredor_50m.csv](../geospatial/resumen_dentro_corredor_50m.csv) | 2 | 2 | 0 |
| [resumen_gravedad_siniestro.csv](../geospatial/resumen_gravedad_siniestro.csv) | 2 | 2 | 0 |
| [segmentos.csv](../geospatial/segmentos.csv) | 26 | 4 | 0 |
| [zonas.csv](../geospatial/zonas.csv) | 439 | 6 | 0 |

## Comprobaciones

```json
{
  "rows": 8332,
  "unique_ids": true,
  "categories": {
    "resto_manrique": 7684,
    "principal_50m": 604,
    "sensibilidad_borde": 40,
    "revision_territorial": 4
  },
  "frozen_ids_equal": {
    "principal_50m": true,
    "sensibilidad_borde": true,
    "revision_territorial": true
  },
  "years": {
    "2019": 1524,
    "2020": 1142,
    "2021": 1413,
    "2022": 1317,
    "2023": 942,
    "2024": 849,
    "2025": 1145
  },
  "months": 84,
  "severity": {
    "HERIDOS": 6781,
    "DAÑOS": 1551
  },
  "types": {
    "CHOQUE": 3711,
    "OTRO": 2046,
    "ATROPELLO": 1513,
    "CAIDA OCUPANTE": 536,
    "VOLCAMIENTO": 526
  },
  "nominal_territories": 18,
  "geometric_territories": {
    "03:Manrique": 8288,
    "04:Aranjuez": 40,
    "90:Corregimiento de Santa Elena": 3,
    "01:Popular": 1
  },
  "zones": 439,
  "zone_nulls": 44,
  "priority_zones": 12,
  "priority_zone_ids_match": true,
  "zone_counts_equal": true,
  "segments": 26,
  "fragments": 6,
  "missing_zone_fk": [],
  "missing_segment_fk": [],
  "missing_category_fk": [],
  "supplement": {
    "rows": 8332,
    "unique_ids": true,
    "missing_join_dates": 0,
    "valid_coordinate_ranges": true,
    "invalid_dates": 0,
    "start": "2019-01-01",
    "end": "2025-12-31",
    "ids_equal": true,
    "year_matches": true,
    "month_matches": true
  },
  "principal_severity": {
    "HERIDOS": 534,
    "DAÑOS": 70
  },
  "principal_types": {
    "CHOQUE": 288,
    "ATROPELLO": 172,
    "OTRO": 93,
    "CAIDA OCUPANTE": 30,
    "VOLCAMIENTO": 21
  },
  "principal_by_year": {
    "2019": 86,
    "2020": 45,
    "2021": 36,
    "2022": 115,
    "2023": 111,
    "2024": 95,
    "2025": 116
  },
  "dimension_keys_unique": {
    "zonas": true,
    "segmentos": true,
    "categorias_analisis": true,
    "fragmentos_revision": true
  },
  "geojson_inventory": {
    "carrera45.geojson": {
      "features": 26,
      "bytes": 7527
    },
    "concentraciones.geojson": {
      "features": 342,
      "bytes": 175511
    },
    "fragmentos_revision.geojson": {
      "features": 6,
      "bytes": 1805
    },
    "zonas_prioritarias.geojson": {
      "features": 12,
      "bytes": 5714
    }
  },
  "unchanged": true
}
```

## Columnas y perfil real

### categorias_analisis.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| categoria_analisis | str | 0 | 5 |
| descripcion | str | 0 | 5 |
| incluye_indicador_principal | bool | 0 | 2 |
| requiere_revision_territorial | bool | 0 | 2 |

### fragmentos_revision.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| parte_id | str | 0 | 6 |
| objectid | int64 | 0 | 4 |
| parte | int64 | 0 | 2 |
| longitud_m | float64 | 0 | 6 |
| diminuta | bool | 0 | 1 |
| clasificacion | str | 0 | 1 |
| decision_version | str | 0 | 1 |
| origen_documentado | str | 0 | 1 |

### hechos_siniestros.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| evento_id | int64 | 0 | 8332 |
| anio | int64 | 0 | 7 |
| mes_numero | int64 | 0 | 12 |
| clase_siniestro | str | 0 | 5 |
| gravedad_siniestro | str | 0 | 2 |
| barrio | str | 0 | 18 |
| num_comuna | str | 0 | 1 |
| fecha_valida | bool | 0 | 1 |
| coordenada_valida | bool | 0 | 1 |
| distancia_carrera45_m | float64 | 0 | 3875 |
| dentro_manrique | bool | 0 | 2 |
| dentro_corredor_50m | bool | 0 | 2 |
| segmento_cercano_id | int64 | 0 | 26 |
| zona_id | str | 44 | 439 |
| categoria_analisis | str | 0 | 4 |
| es_indicador_principal | bool | 0 | 2 |
| sensibilidad_borde | bool | 0 | 2 |
| pendiente_revision_territorial | bool | 0 | 2 |
| distancia_limite_manrique_m | float64 | 0 | 3875 |
| territorio_geometrico | str | 0 | 4 |

### resumen_anio.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| anio | int64 | 0 | 7 |
| cantidad | int64 | 0 | 7 |

### resumen_anio_categoria.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| anio | int64 | 0 | 7 |
| categoria_analisis | str | 0 | 4 |
| cantidad | int64 | 0 | 17 |

### resumen_barrio.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| barrio | str | 0 | 18 |
| cantidad | int64 | 0 | 18 |

### resumen_categoria_analisis.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| categoria_analisis | str | 0 | 4 |
| cantidad | int64 | 0 | 4 |

### resumen_clase_siniestro.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| clase_siniestro | str | 0 | 5 |
| cantidad | int64 | 0 | 5 |

### resumen_dentro_corredor_50m.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| dentro_corredor_50m | bool | 0 | 2 |
| cantidad | int64 | 0 | 2 |

### resumen_gravedad_siniestro.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| gravedad_siniestro | str | 0 | 2 |
| cantidad | int64 | 0 | 2 |

### segmentos.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| segmento_cercano_id | int64 | 0 | 26 |
| longitud_m | float64 | 0 | 26 |
| valida | bool | 0 | 1 |
| duplicada | bool | 0 | 1 |

### zonas.csv

| Columna | Tipo inferido | Nulos | Distintos |
|---|---|---:|---:|
| zona_id | str | 0 | 439 |
| cantidad | int64 | 0 | 67 |
| heridos | int64 | 0 | 61 |
| muertos | int64 | 0 | 1 |
| cerca_100m | int64 | 0 | 33 |
| prioritaria | bool | 0 | 2 |
