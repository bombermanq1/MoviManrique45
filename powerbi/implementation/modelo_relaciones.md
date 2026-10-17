# Modelo y relaciones para Power BI Desktop

## Principio de modelado

El grano de `FactSiniestros` es **un evento por `evento_id`**. Debe cargar
exactamente 8.332 filas. No anexe tablas de resumen, fragmentos, segmentos ni
zonas a los hechos: hacerlo duplicaría eventos y rompería los indicadores 604,
40, 4 y 7.684.

Las consultas M añaden en memoria fecha, latitud y longitud a partir de la
fuente procesada ya existente mediante una unión validada 1:1. No modifican los
CSV ni cambian la clasificación geoespacial.

## Tablas que se cargan

| Tabla | Filas esperadas | Clave | Rol |
|---|---:|---|---|
| `FactSiniestros` | 8.332 | `evento_id` | Hechos a nivel de evento |
| `DimFecha` | 2.557 | `Fecha` | Calendario continuo 2019–2025 |
| `DimTerritorioNominal` | 18 | `TerritorioId` | Pares originales comuna/barrio |
| `DimTerritorioGeometrico` | 4 | `TerritorioGeometrico` | Resultado territorial geométrico |
| `DimGravedad` | 2 | `gravedad_siniestro` | Gravedad observada |
| `DimTipo` | 5 | `clase_siniestro` | Clase de siniestro observada |
| `DimClasificacion` | 5 | `categoria_analisis` | Principal, borde, revisión, resto y reserva |
| `DimZona` | 440 | `zona_id` | 439 celdas más `SIN_ZONA` para 44 eventos |
| `DimSegmento` | 26 | `segmento_cercano_id` | Segmento vial más cercano; no atribución causal |
| `DimIdsCongelados` | 648 | categoría + ID | Control desconectado 604/40/4 |
| `RevisionFragmentos` | 6 | `parte_id` | Seis fragmentos preservados para trazabilidad |

## Relaciones que deben crearse manualmente

Configure todas como **activas**, cardinalidad **uno a varios (1:*)** y filtro
en una sola dirección desde la dimensión. Desactive relaciones automáticas
adicionales antes de aplicar esta lista.

| Desde (lado 1) | Hacia (lado *) | Relación | Filtro |
|---|---|---|---|
| `DimFecha[Fecha]` | `FactSiniestros[fecha_siniestro]` | 1:* | Único |
| `DimTerritorioNominal[TerritorioId]` | `FactSiniestros[TerritorioId]` | 1:* | Único |
| `DimTerritorioGeometrico[TerritorioGeometrico]` | `FactSiniestros[territorio_geometrico]` | 1:* | Único |
| `DimGravedad[gravedad_siniestro]` | `FactSiniestros[gravedad_siniestro]` | 1:* | Único |
| `DimTipo[clase_siniestro]` | `FactSiniestros[clase_siniestro]` | 1:* | Único |
| `DimClasificacion[categoria_analisis]` | `FactSiniestros[categoria_analisis]` | 1:* | Único |
| `DimZona[zona_id]` | `FactSiniestros[zona_id_modelo]` | 1:* | Único |
| `DimSegmento[segmento_cercano_id]` | `FactSiniestros[segmento_cercano_id]` | 1:* | Único |
| `DimSegmento[segmento_cercano_id]` | `RevisionFragmentos[objectid]` | 1:* | Único |

`DimIdsCongelados` es deliberadamente **desconectada**. No cree una relación
con `FactSiniestros`: se usa en la medida de comparación exacta de IDs y una
relación alteraría filtros/indicadores.

No cree relaciones N:N, bidireccionales ni entre tablas de resumen y hechos.
No conecte `DimTerritorioNominal` con `DimTerritorioGeometrico`; representan
conceptos distintos y conectarlas introduce rutas ambiguas.

## Configuración semántica posterior a las relaciones

1. Marque `DimFecha` como tabla de fechas usando `Fecha`.
2. Ordene `DimFecha[Mes]` por `MesNumero`, `AñoMes` por `OrdenAñoMes` y
   `Trimestre` por `TrimestreNumero`.
3. Categorice `FactSiniestros[latitud]` como latitud y `longitud` como longitud;
   no los resuma. `evento_id`, claves y distancias tampoco se resumen.
4. Oculte claves técnicas, `zona_id_modelo`, flags duplicados y
   `DimIdsCongelados` del panel de campos para usuarios finales, pero no los
   borre.
5. Mantenga `DimZona[cantidad]`, `heridos`, `muertos` y `cerca_100m` como
   atributos estáticos del cierre; no los use para sumar datos al filtrar años.

## Conciliación obligatoria antes de construir visuales

Sin filtros, las tarjetas/consultas deben devolver:

| Control | Resultado |
|---|---:|
| `Registros` | 8.332 |
| `Registros corredor` | 604 |
| `Registros sensibilidad borde` | 40 |
| `Registros revisión territorial` | 4 |
| `Registros resto Manrique` | 7.684 |
| `Zonas prioritarias de la versión` | 12 |
| `Fragmentos conservados de la versión` | 6 |
| `Registros sin zona` | 44 |
| `Conteo IDs congelados principal` | 604 |
| `Integridad IDs principal` | OK — 604 IDs congelados coinciden |

Si alguno difiere, revise las consultas y las relaciones; no corrija el dato
mediante filtros ocultos, `Remove Duplicates`, uniones internas ni reemplazos.

## Semántica que debe conservarse

- 604 es el indicador territorial estricto y **no** equivale a los 644 casos de
  proximidad simple a 50 m.
- Los 40 casos de borde se muestran como sensibilidad, nunca se suman al
  indicador principal.
- Las cuatro filas de revisión territorial no son casos de Manrique agregados al
  corredor.
- La cercanía al eje es una relación espacial, no una prueba de causalidad vial.
- La ausencia de registros de fallecidos en esta fuente no debe traducirse a una
  conclusión sobre personas fallecidas.
