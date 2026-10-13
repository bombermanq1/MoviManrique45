# Preparación propuesta para Power BI Desktop

No se ejecutaron estas transformaciones en Power Query. Son especificaciones y
fragmentos para la siguiente etapa, sin modificar los CSV ni crear PBIX/PBIP.

## Compatibilidad comprobada y límites

Los 12 CSV se leen correctamente en UTF-8, separados por coma, con cabecera,
decimales con punto y valores booleanos True/False. Hay archivos con y sin BOM.
No hay filas completas duplicadas; evento_id es único. Los tipos inferidos del
[inventario](auditoria.md) no sustituyen los tipos explícitos del modelo.

Fecha y coordenadas proceden del CSV procesado ya existente: 8332 correspondencias
1:1 por ID, sin fechas faltantes, con año/mes coherentes. No se debe obtener la
fecha asignando arbitrariamente el primer día del mes. No se requiere conexión
a PostgreSQL para el modelo propuesto ni duplicar las operaciones geoespaciales.

## Parámetros y consultas de preparación

Crear en Desktop, posteriormente, parámetro de texto `pRaiz` apuntando a la raíz
local del proyecto. No incluir credenciales. Consultas Stg* y funciones: desactivar
carga; solo cargar FactSiniestros, dimensiones y RevisionFragmentos.

### Función fxCsv

```powerquery
(ruta as text) as table =>
let
    Fuente = Csv.Document(File.Contents(ruta),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Cabeceras = Table.PromoteHeaders(Fuente, [PromoteAllScalars=true])
in
    Cabeceras
```

No usar detección automática de tipos como resultado final. El conector permite
definir separador y codificación. [Csv.Document, Microsoft](https://learn.microsoft.com/en-us/powerquery-m/csv-document).

### StgHechos

```powerquery
let
    Fuente = fxCsv(pRaiz & "/powerbi/geospatial/hechos_siniestros.csv"),
    Tipos = Table.TransformColumnTypes(Fuente, {
        {"evento_id", type text}, {"anio", Int64.Type}, {"mes_numero", Int64.Type},
        {"clase_siniestro", type text}, {"gravedad_siniestro", type text},
        {"barrio", type text}, {"num_comuna", type text},
        {"segmento_cercano_id", Int64.Type}, {"zona_id", type text},
        {"categoria_analisis", type text}, {"territorio_geometrico", type text},
        {"distancia_carrera45_m", type number}, {"distancia_limite_manrique_m", type number}
    }, "en-US"),
    Flags = {"fecha_valida", "coordenada_valida", "dentro_manrique",
        "dentro_corredor_50m", "es_indicador_principal", "sensibilidad_borde",
        "pendiente_revision_territorial"},
    Logicos = Table.TransformColumns(Tipos,
        List.Transform(Flags, (c) => {c,
            (v) => if v = null or v = "" then null else Logical.FromText(Text.Lower(v)),
            type nullable logical})),
    Unicos = List.Count(List.Distinct(Logicos[evento_id])) = Table.RowCount(Logicos),
    Resultado = if not Unicos or List.Contains(Logicos[evento_id], null)
        or List.Contains(Logicos[evento_id], "")
        then error "evento_id nulo o duplicado; no quitar duplicados automaticamente."
        else Logicos
in
    Resultado
```

No recortar, renombrar ni normalizar categorías del cierre salvo nombres de
columnas del modelo; no reemplazar IDs, distancias ni flags aprobados.

### StgFechaCoordenadas

```powerquery
let
    Fuente = fxCsv(pRaiz & "/data/processed/siniestros_comuna3_limpios.csv"),
    Columnas = Table.SelectColumns(Fuente,
        {"objectid", "fecha_siniestro", "latitud", "longitud"}),
    Tipos = Table.TransformColumnTypes(Columnas,
        {{"objectid", type text}, {"latitud", type number}, {"longitud", type number}}, "en-US"),
    Fechas = Table.TransformColumns(Tipos,
        {{"fecha_siniestro", each Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]), type date}}),
    Resultado = if List.Count(List.Distinct(Fechas[objectid])) <> Table.RowCount(Fechas)
        then error "El auxiliar tiene IDs duplicados. No expandir una relacion 1:N."
        else Fechas
in
    Resultado
```

### StgConFecha: unión 1:1 propuesta

```powerquery
let
    Union = Table.NestedJoin(StgHechos, {"evento_id"},
        StgFechaCoordenadas, {"objectid"}, "Aux", JoinKind.LeftOuter),
    Matches = Table.AddColumn(Union, "Matches", each Table.RowCount([Aux]), Int64.Type),
    Control = if List.AnyTrue(List.Transform(Matches[Matches], each _ <> 1))
        then error "Hay eventos sin coincidencia o con multiples filas auxiliares."
        else Matches,
    Expandida = Table.ExpandTableColumn(Control, "Aux",
        {"fecha_siniestro", "latitud", "longitud"}),
    FechasCoherentes = Table.AddColumn(Expandida, "FechaCoherente",
        each Date.Year([fecha_siniestro]) = [anio] and Date.Month([fecha_siniestro]) = [mes_numero], type logical),
    ControlFecha = if List.Contains(FechasCoherentes[FechaCoherente], false)
        then error "Fecha auxiliar no concuerda con el periodo validado." else FechasCoherentes,
    ZonaModelo = Table.AddColumn(ControlFecha, "zona_id_modelo",
        each if [zona_id] = null or [zona_id] = "" then "SIN_ZONA" else [zona_id], type text),
    Resultado = Table.RemoveColumns(ZonaModelo, {"Matches", "FechaCoherente"})
in
    Resultado
```

Verificar 8332 antes y después y conjunto exacto de IDs; no resolver fallos con
inner join, quitar duplicados o borrar filas. Esto cambia solo el modelo en
memoria que se construirá, no los archivos validados.

### DimTerritorioNominal y FactSiniestros

```powerquery
// Consulta DimTerritorioNominal; no depende de FactSiniestros
let
    Pares = Table.Distinct(Table.SelectColumns(StgConFecha, {"num_comuna", "barrio"})),
    Orden = Table.Sort(Pares, {{"num_comuna", Order.Ascending}, {"barrio", Order.Ascending}}),
    Clave = Table.AddIndexColumn(Orden, "TerritorioId", 1, 1, Int64.Type)
in
    Clave
```

```powerquery
// Consulta FactSiniestros; relacionar por TerritorioId despues de cargar
let
    Union = Table.NestedJoin(StgConFecha, {"num_comuna", "barrio"},
        DimTerritorioNominal, {"num_comuna", "barrio"}, "Dim", JoinKind.LeftOuter),
    Control = if List.AnyTrue(List.Transform(Union[Dim], each Table.RowCount(_) <> 1))
        then error "Dimension territorial no univoca." else Union,
    Resultado = Table.ExpandTableColumn(Control, "Dim", {"TerritorioId"})
in
    Resultado
```

El índice territorial es una clave del modelo, no un código oficial; reconstruir
dimensión y hechos juntos en cada refresh. No concatenar barrio/comuna sin
escapado y asumir que la clave es universal. DimGravedad, DimTipo y
DimTerritorioGeometrico se obtienen por referencia a StgConFecha seleccionando
su columna natural y aplicando Table.Distinct; no dependen de FactSiniestros.
Renombrar la clave geométrica como TerritorioGeometrico en la dimensión.

### DimFecha

```powerquery
let
    Inicio = Date.StartOfYear(List.Min(StgConFecha[fecha_siniestro])),
    Fin = Date.EndOfYear(List.Max(StgConFecha[fecha_siniestro])),
    Lista = List.Dates(Inicio, Duration.Days(Fin-Inicio)+1, #duration(1,0,0,0)),
    Base = Table.FromColumns({Lista}, type table [Fecha=date]),
    Anio = Table.AddColumn(Base, "Año", each Date.Year([Fecha]), Int64.Type),
    MesNum = Table.AddColumn(Anio, "MesNumero", each Date.Month([Fecha]), Int64.Type),
    Mes = Table.AddColumn(MesNum, "Mes", each Date.MonthName([Fecha], "es-CO"), type text),
    AnioMes = Table.AddColumn(Mes, "AñoMes", each Date.ToText([Fecha], "yyyy-MM"), type text),
    Orden = Table.AddColumn(AnioMes, "OrdenAñoMes", each [Año]*100+[MesNumero], Int64.Type)
in
    Orden
```

Esperado: 2557 fechas únicas continuas. Marcar tabla de fechas en Desktop;
ordenar Mes por MesNumero y AñoMes por OrdenAñoMes. Desactivar fecha/hora
automática para este modelo. Agregar trimestre si se utilizará; no es obligatorio.

### Dimensiones existentes y tabla de revisión

| Consulta | Preparación propuesta |
|---|---|
| DimClasificacion | categorias_analisis.csv; clave texto única, descripción texto, flags lógicos; conservar cinco filas |
| DimSegmento | segmentos.csv; clave Int64, longitud decimal en-US, flags lógicos; 26 filas |
| DimZona | zonas.csv; clave texto, conteos Int64, prioritaria lógica; añadir una fila SIN_ZONA, conteos nulos, prioritaria=false; 440 filas de modelo |
| RevisionFragmentos | fragmentos_revision.csv; parte_id texto único, objectid/parte Int64, longitud decimal, diminuta lógica, demás campos texto; seis filas |

Los CSV resumen permanecen sin carga al modelo; se usan para conciliación en
esta etapa y durante las pruebas. No construir relaciones entre tablas resumen.

## Construcción futura en Desktop, paso a paso

1. Tras autorización de implementación, abrir Desktop y crear un reporte local.
2. Definir pRaiz, consultas Stg*, dimensiones y tabla de hechos conforme a esta
   propuesta. No ejecutar cargas a SQL ni scripts de corrección geoespacial.
3. Inspeccionar errores de conversión, claves y conteos antes de Cerrar y aplicar.
4. Crear manualmente las nueve relaciones de [modelo.md](modelo.md), todas 1:N
   y unidireccionales; eliminar relaciones automáticas ambiguas si aparecen.
5. Marcar DimFecha, configurar ordenamientos y categorías latitud/longitud;
   ocultar campos técnicos y columnas estáticas que inducen sumas incorrectas.
6. Crear y validar [medidas DAX](medidas_dax.md) una a una. Conciliar 8332,604,40,4
   y los casos de filtros documentados. Distinguir cero, vacío y no disponible.
7. Construir las cuatro páginas según [dashboard.md](dashboard.md). Configurar
   sincronización de segmentadores, interacciones y botones de restablecimiento.
8. Probar mapa de puntos y referencias de líneas/polígonos. Confirmar permisos
   del visual Azure Maps y correspondencia de zona_id; no asumir que los 342
   polígonos exportables representan todas las 439 celdas.
9. Revisar accesibilidad, tooltips, navegación y efectos de filtros; comprobar
   que principal nunca incorpora los 40 casos de sensibilidad.
10. Guardar y reabrir; refrescar desde los CSV originales sin modificarlos.
    Solo declarar funcional después de esos controles. No publicar sin autorización.

## Viabilidad de PBIP

Inspección local: Power BI Desktop Store **2.158.1304.0** está instalado. Las
herramientas disponibles permiten escribir/validar archivos de texto y ejecutar
comprobaciones locales, por lo que la generación programática es técnicamente
plausible. No se ha verificado todavía en Desktop un proyecto generado ni la
compatibilidad de sus objetos visuales. Esta etapa no crea PBIP, PBIX ni TMDL.

Microsoft documenta las definiciones textuales de modelo/reporte, la autoría
programática y la reapertura en Desktop. La conversión PBIX↔PBIP se realiza con
Guardar como de Desktop, no mediante una conversión programática equivalente.
Para la futura implementación conviene partir de un proyecto mínimo guardado
por la instalación local, seguir los esquemas oficiales y verificar apertura,
refresh, DAX, relaciones y render. No basta validar JSON para garantizar un reporte.
[Documentación oficial PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

El workspace actual está sincronizado con OneDrive. Microsoft advierte posibles
fallos de sincronización al guardar PBIP en carpetas sincronizadas; evaluar una
carpeta local corta en la fase de construcción. No se ha movido el proyecto ni
alterado su configuración. La habilitación de funciones y Azure Maps en esta
instalación/organización queda por comprobar.

## Pendientes que no impiden aprobar el diseño

- Validar M y DAX en el motor de Desktop; aquí son propuestas, no resultados ejecutados.
- Confirmar visibilidad/interacción de mapas y autorización del detalle geográfico.
- Confirmar que el dashboard usará la unión auxiliar de fecha/coordenadas propuesta;
  ya es compatible y unívoca, pero no se aplicó al dataset.
- Mantener las decisiones de borde, fragmentos y CRS del cierre geoespacial.
