# Medidas DAX propuestas — pendientes de ejecución en Desktop

Usan las tablas de [modelo.md](modelo.md). Crear cada medida por separado.
Los conteos esperados se comprobaron en los CSV; el código DAX todavía no se
compiló ni ejecutó en un modelo Power BI. Ajustar separadores según configuración
regional del editor, sin cambiar el significado.

## Conteos y distribución

```dax
Registros = COUNTROWS(FactSiniestros)

Registros corredor =
CALCULATE(
    [Registros],
    REMOVEFILTERS(DimClasificacion),
    DimClasificacion[categoria_analisis] = "principal_50m"
)

Registros sensibilidad =
CALCULATE(
    [Registros],
    REMOVEFILTERS(DimClasificacion),
    DimClasificacion[categoria_analisis] = "sensibilidad_borde"
)

Registros revision territorial =
CALCULATE(
    [Registros],
    REMOVEFILTERS(DimClasificacion),
    DimClasificacion[categoria_analisis] = "revision_territorial"
)

Porcentaje gravedad en seleccion =
DIVIDE([Registros], CALCULATE([Registros], REMOVEFILTERS(DimGravedad)))

Porcentaje tipo en seleccion =
DIVIDE([Registros], CALCULATE([Registros], REMOVEFILTERS(DimTipo)))
```

Las tres medidas por categoría fijan su propia categoría, incluso cuando un
segmentador de clasificación selecciona otra. Es deliberado para tarjetas de
comparación; no usar esas medidas en una matriz por categoría que deba sumar sus
filas. Allí usar [Registros]. No poner filtros sobre flags o categoria_analisis
de FactSiniestros: ocultarlos y usar dimensiones; así no quedan filtros ocultos
contradictorios. Gravedad/tipo por año usan [Registros] con los ejes de dimensión,
no hacen falta medidas duplicadas para cada año o etiqueta.

## Porcentaje del corredor respecto a Comuna 3

Mantiene fecha, gravedad y tipo; ignora filtros de barrio, territorio geométrico,
zona, segmento y categoría en **ambos** términos. Mostrar ese alcance en tooltip.

```dax
Comuna 3 comparable =
CALCULATE(
    [Registros],
    REMOVEFILTERS(DimClasificacion),
    REMOVEFILTERS(DimTerritorioNominal),
    REMOVEFILTERS(DimTerritorioGeometrico),
    REMOVEFILTERS(DimZona),
    REMOVEFILTERS(DimSegmento)
)

Corredor comparable =
CALCULATE(
    [Registros corredor],
    REMOVEFILTERS(DimTerritorioNominal),
    REMOVEFILTERS(DimTerritorioGeometrico),
    REMOVEFILTERS(DimZona),
    REMOVEFILTERS(DimSegmento)
)

Porcentaje corredor sobre Comuna 3 =
DIVIDE([Corredor comparable], [Comuna 3 comparable])
```

Resultado sin filtros: 604/8332 = 7.249159866%, mostrar **7.25%**. La selección
nominal incluye los 44 externos: no usar 8288 como denominador sin cambiar el
nombre y la definición del indicador. Evitar filtros de página principal=true,
que harían que un porcentaje ingenuo devolviera 100%.

## Comparaciones temporales descriptivas

Requieren DimFecha diaria continua, relación activa por fecha real y marcada
como tabla de fechas. La selección actual debe representar un período comparable.

```dax
Registros mismo periodo anterior =
CALCULATE([Registros], SAMEPERIODLASTYEAR(DimFecha[Fecha]))

Cambio absoluto anual =
VAR Anterior = [Registros mismo periodo anterior]
RETURN IF(ISBLANK(Anterior), BLANK(), [Registros] - Anterior)

Cambio porcentual anual =
VAR Anterior = [Registros mismo periodo anterior]
RETURN IF(ISBLANK(Anterior), BLANK(), DIVIDE([Registros] - Anterior, Anterior))

Corredor mismo periodo anterior =
CALCULATE([Registros corredor], SAMEPERIODLASTYEAR(DimFecha[Fecha]))

Cambio porcentual corredor =
VAR Anterior = [Corredor mismo periodo anterior]
RETURN IF(ISBLANK(Anterior), BLANK(), DIVIDE([Registros corredor] - Anterior, Anterior))
```

2019 no dispone de 2018: mostrar vacío/no disponible, no cero ni -100%. Evitar
convertir todas las medidas base a cero con COALESCE; usarlo solo en tarjetas de
presentación donde ausencia de filas realmente signifique cero. Diferencias
anuales son conteos registrados, no cambios de riesgo o efectos de intervenciones.

## Geografía y calidad

```dax
Mediana distancia corredor m =
CALCULATE(
    MEDIAN(FactSiniestros[distancia_carrera45_m]),
    REMOVEFILTERS(DimClasificacion),
    DimClasificacion[categoria_analisis] = "principal_50m"
)

Zonas prioritarias de la version =
CALCULATE(
    COUNTROWS(DimZona),
    REMOVEFILTERS(DimZona),
    DimZona[prioritaria] = TRUE()
)

Zonas prioritarias con registros en seleccion =
COUNTROWS(
    FILTER(
        FILTER(DimZona, DimZona[prioritaria] = TRUE()),
        CALCULATE([Registros]) > 0
    )
)

Fragmentos conservados de la version =
CALCULATE(COUNTROWS(RevisionFragmentos), REMOVEFILTERS(DimSegmento), REMOVEFILTERS(RevisionFragmentos))

Registros sin zona =
CALCULATE([Registros], REMOVEFILTERS(DimZona), DimZona[zona_id] = "SIN_ZONA")

Registros con coordenada validada =
CALCULATE([Registros], FactSiniestros[coordenada_valida] = TRUE())
```

Prioridades de versión =12, fragmentos=6; son atributos del cierre y no deben
variar al filtrar años de eventos. El conteo de zonas con registros sí responde
a filtros. La medida de coordenadas expresa rango/validación de la fuente, no
exactitud geográfica ni pertenencia territorial. No sumar zonas.cantidad como
medida temporal. No sumar longitudes viales en la tabla de hechos.

## Casos de aceptación propuestos

| Contexto | Resultado esperado |
|---|---|
| Sin filtros | Registros=8332, corredor=604, sensibilidad=40, revisión=4 |
| Año=2025 | Registros=1145, corredor=116 |
| Gravedad HERIDOS, sin otros filtros | Registros=6781, corredor=534 |
| Tipo ATROPELLO | Registros=1513, corredor=172 |
| Matriz por categoría con [Registros] | 604+40+4+7684=8332 |
| Porcentaje global sin filtros | 7.25%, nunca 100% por filtro accidental |
| Primer año 2019, variación anual | No disponible |
| Zona SIN_ZONA sin otros filtros | 44 |

Se probarán además selecciones múltiples y cero filas en Desktop. No se incluyen
tasas de accidentalidad, exposición, víctimas ni inferencias causales.
