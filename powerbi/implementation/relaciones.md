# Relaciones de implementación

Archivo de referencia rápida. La explicación de grano, tipos, configuración y
controles está en [modelo_relaciones.md](modelo_relaciones.md).

Todas las relaciones son activas, **1:* y unidireccionales desde dimensión**:

| Desde | Hacia |
|---|---|
| `DimFecha[Fecha]` | `FactSiniestros[fecha_siniestro]` |
| `DimTerritorioNominal[TerritorioId]` | `FactSiniestros[TerritorioId]` |
| `DimTerritorioGeometrico[TerritorioGeometrico]` | `FactSiniestros[territorio_geometrico]` |
| `DimGravedad[gravedad_siniestro]` | `FactSiniestros[gravedad_siniestro]` |
| `DimTipo[clase_siniestro]` | `FactSiniestros[clase_siniestro]` |
| `DimClasificacion[categoria_analisis]` | `FactSiniestros[categoria_analisis]` |
| `DimZona[zona_id]` | `FactSiniestros[zona_id_modelo]` |
| `DimSegmento[segmento_cercano_id]` | `FactSiniestros[segmento_cercano_id]` |
| `DimSegmento[segmento_cercano_id]` | `RevisionFragmentos[objectid]` |

`DimIdsCongelados` no lleva relación: es una tabla desconectada usada para la
comparación exacta de los 604 IDs en DAX. No crear relaciones N:N,
bidireccionales, entre dimensiones territoriales ni entre resúmenes y hechos.

Antes de aplicar el modelo, actualice `ControlCierreEstricto` y compruebe
8.332/604/40/4/7.684. Si falla, detenga la carga: no resuelva el problema con
uniones internas ni eliminando filas.
