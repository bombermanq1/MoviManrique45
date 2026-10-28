# Recursos opcionales para Power BI

El dashboard web de MoviManrique45 funciona por separado y no necesita Power BI.
La carpeta [powerbi/implementation](../powerbi/implementation) contiene
consultas, medidas y una propuesta de modelo para construir un informe en
Power BI Desktop. Son recursos de implementación manual: no hay un archivo
PBIX o PBIP validado en Desktop, ni se han comprobado allí la ejecución de las
consultas, las medidas, las relaciones o los visuales.

## Antes de comenzar

Se necesitan Power BI Desktop y los archivos locales del proyecto, incluidos los
datos procesados del cierre. La [guía de instalación](instalacion.md) explica cómo comprobar los insumos
que no se incluyen en Git. Las consultas leen archivos locales y no
requieren PostgreSQL ni modifican las fuentes.

Los recursos principales son:

- [Consultas Power Query independientes](../powerbi/implementation/powerquery).
- [Medidas DAX del modelo](../powerbi/implementation/dax/medidas_modelo.dax).
- [IDs de referencia del cierre](../src/geospatial/ids_cierre_v1.json).
- [Validador estático](../powerbi/implementation/validar_recursos_powerbi.py).

El archivo `consultas_powerquery.m` es un índice; no debe pegarse como si fuera
una única consulta completa. Cada archivo `.m` de `powerquery/` corresponde a
una consulta o función independiente.

## Preparar las consultas

En Power BI Desktop, cree una consulta en blanco por cada archivo y pegue su
contenido en el Editor avanzado. Use el nombre del archivo sin el prefijo
numérico. Siga este orden:

1. Cree el parámetro de texto `pRaiz` con la ruta local a la raíz del proyecto,
   sin credenciales ni barra final. La plantilla correspondiente está en
   [00_parametro_pRaiz.m.template](../powerbi/implementation/powerquery/00_parametro_pRaiz.m.template).
2. Cree las funciones `fxRutaProyecto`, `fxCsv`, `fxBool` y `fxControlTabla`
   con los archivos 01 a 04; desactive su carga.
3. Cree `StgHechos`, `StgFechaCoordenadas` y `StgConFecha` con los archivos
   10 a 12; desactive su carga.
4. Cree las dimensiones y `RevisionFragmentos` con los archivos 20 a 29.
   Después cree `FactSiniestros` con el archivo 30.
5. Cree `ValidacionCierre` y `ControlCierreEstricto` con los archivos 40 y 41.
   Manténgalas sin carga, ábralas y actualícelas antes de aplicar cambios.
   `ControlCierreEstricto` debe detener el proceso si un control falla.

Cargue al modelo `FactSiniestros`, `DimFecha`, `DimTerritorioNominal`,
`DimTerritorioGeometrico`, `DimGravedad`, `DimTipo`, `DimClasificacion`,
`DimZona`, `DimSegmento`, `DimIdsCongelados` y `RevisionFragmentos`.
`DimIdsCongelados` es una tabla desconectada para comprobar los IDs: ocúltela
del panel de campos, pero no la elimine ni cree relaciones con ella.

## Crear las relaciones

Las nueve relaciones propuestas son activas, de uno a varios y con filtro
unidireccional desde la dimensión. Evite relaciones automáticas adicionales,
bidireccionales o de muchos a muchos.

| Desde: lado 1 | Hacia: lado varios |
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

El grano de `FactSiniestros` es un registro por `evento_id`. No anexe
resúmenes, fragmentos, segmentos ni zonas a la tabla de hechos, pues se
duplicarían eventos. El territorio nominal y el geométrico representan
conceptos distintos y no deben relacionarse directamente entre sí.

Marque `DimFecha` como tabla de fechas. Ordene `Mes` por `MesNumero`, `AñoMes`
por `OrdenAñoMes` y `Trimestre` por `TrimestreNumero`. Categorice `latitud` y
`longitud` como coordenadas y no las resuma. Los conteos de `DimZona` son
atributos fijos del cierre: no deben sumarse como si respondieran a los
filtros temporales de los eventos.

## Medidas y controles

Cree cada medida del archivo DAX por separado. Las medidas de corredor, borde
y revisión fijan su categoría y conservan los demás filtros; para una matriz
por categoría utilice la medida `Registros`.

`Porcentaje corredor sobre Comuna 3` usa un denominador comparable: conserva
los filtros de fecha, tipo y gravedad, pero ignora los de clasificación,
territorio nominal y geométrico, zona y segmento. No lo presente como un
porcentaje específico del barrio o zona seleccionado.

Antes de crear visuales, compruebe sin filtros:

| Control | Resultado esperado |
|---|---:|
| Siniestros en los hechos | 8.332 |
| Corredor territorial estricto | 604 |
| Sensibilidad al borde | 40 |
| Revisión territorial | 4 |
| Resto de Manrique | 7.684 |
| Segmentos del eje | 26 |
| Celdas analíticas / zonas exploratorias | 439 / 12 |
| Fragmentos conservados | 6 |
| Registros sin zona | 44 |

Compruebe también la coincidencia exacta de los IDs de las categorías 604/40/4,
no solo sus cantidades. La medida `Integridad IDs principal` debe indicar que
los 604 IDs congelados coinciden. Si falla cualquier control, detenga la carga
y revise las fuentes y relaciones; no elimine filas ni cambie clasificaciones
para ajustar las cifras.

La unión de fecha y coordenadas debe ser 1:1 y conservar los 8.332 eventos.
Las 40 observaciones de sensibilidad y las cuatro de revisión no se suman al
indicador estricto de 604. Los 644 casos de proximidad simple a 50 m son una
comparación metodológica, no el indicador territorial estricto.

## Construir y verificar el informe

La propuesta contempla cuatro páginas:

1. **Resumen general:** use filtros de año y barrio, tarjetas con `Registros`,
   `Registros corredor` y `Porcentaje corredor sobre Comuna 3`; agregue la
   serie por año, barras por gravedad y tipo, y una matriz de año por
   clasificación.
2. **Carrera 45:** muestre `Registros corredor`, el porcentaje comparable y
   `Mediana distancia corredor m`; compare la serie total con la del corredor y
   presente clase y gravedad del indicador estricto. Indique que los 40 casos
   de sensibilidad no forman parte de los 604.
3. **Análisis geográfico:** use latitud, longitud, clasificación y registros;
   agregue una tabla de zonas con `zona_id` y prioridad, manteniendo
   `SIN_ZONA` para los 44 registros correspondientes. Si el visual lo permite,
   pruebe las capas GeoJSON locales antes de incluirlas como referencia.
4. **Calidad y trazabilidad:** presente los controles de borde, revisión,
   fragmentos e integridad de IDs, junto con las limitaciones del análisis.

Sincronice año y barrio en las páginas 1 a 3 y evite que filtros ocultos
distorsionen los controles generales de la página 4. Mantenga las 12 zonas
como exploratorias: no son una tasa de riesgo, obras aprobadas ni una
atribución causal.

Pruebe los filtros de año, barrio, gravedad y tipo, y verifique que los rótulos
distingan los totales filtrados de los generales. Sin filtros, confirme los
controles anteriores. Como comprobaciones adicionales de la versión, en 2025
hay 1.145 registros en los hechos y 116 en el corredor estricto; en la
categoría HERIDOS hay 6.781 y 534, respectivamente.

Guarde el informe, ciérrelo, ábralo de nuevo y actualice los datos. Solo
después de validar consultas, DAX, relaciones, visuales y actualización en
Desktop puede considerarse un PBIX/PBIP funcional.

El validador estático puede ejecutarse desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe powerbi\implementation\validar_recursos_powerbi.py
```

Este comando guarda la evidencia JSON en `powerbi/implementation/` y el reporte
Markdown en `docs/validacion_estatica_powerbi.md`.
Comprueba recursos y datos de forma estática; no sustituye las pruebas en
Power BI Desktop. La proximidad al eje no demuestra causalidad y la ausencia
de una categoría de fallecidos en la fuente no demuestra que no los haya.
