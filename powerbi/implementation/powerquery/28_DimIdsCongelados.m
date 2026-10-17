let
    Origen = Json.Document(File.Contents(fxRutaProyecto("src/geospatial/ids_cierre_v1.json"))),
    Categorias = Record.FieldNames(Origen),
    Registros = List.Combine(
        List.Transform(
            Categorias,
            (categoria as text) => List.Transform(
                Record.Field(Origen, categoria),
                (id as any) => [categoria_analisis = categoria, evento_id = Int64.From(id)]
            )
        )
    ),
    Tabla = Table.FromRecords(Registros, type table [categoria_analisis = text, evento_id = Int64.Type]),
    Ordenada = Table.Sort(Tabla, {{"categoria_analisis", Order.Ascending}, {"evento_id", Order.Ascending}}),
    SinDuplicados = fxControlTabla(
        Ordenada,
        List.Count(List.Distinct(List.Transform(Table.ToRecords(Ordenada), each [categoria_analisis] & ":" & Text.From([evento_id])))) = Table.RowCount(Ordenada),
        "MM45_IDS_CONGELADOS_DUPLICADOS",
        "La lista de IDs congelados no debe contener duplicados por categoría."
    ),
    Conteos = fxControlTabla(
        SinDuplicados,
        Table.RowCount(SinDuplicados) = 648 and
            Table.RowCount(Table.SelectRows(SinDuplicados, each [categoria_analisis] = "principal_50m")) = 604 and
            Table.RowCount(Table.SelectRows(SinDuplicados, each [categoria_analisis] = "sensibilidad_borde")) = 40 and
            Table.RowCount(Table.SelectRows(SinDuplicados, each [categoria_analisis] = "revision_territorial")) = 4,
        "MM45_IDS_CONGELADOS_CONTEOS",
        "La lista de cierre debe conservar exactamente 604/40/4 IDs."
    )
in
    Conteos
