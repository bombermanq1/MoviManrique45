let
    Origen = fxCsv("powerbi/geospatial/zonas.csv"),
    Tipos = Table.TransformColumnTypes(
        Origen,
        {
            {"zona_id", type text}, {"cantidad", Int64.Type}, {"heridos", Int64.Type},
            {"muertos", Int64.Type}, {"cerca_100m", Int64.Type}
        },
        "en-US"
    ),
    Flags = Table.TransformColumns(Tipos, {{"prioritaria", each fxBool(_), type nullable logical}}),
    ZonasBase = fxControlTabla(
        Flags,
        Table.RowCount(Flags) = 439 and
            List.Count(List.Distinct(Flags[zona_id])) = Table.RowCount(Flags) and
            Table.RowCount(Table.SelectRows(Flags, each [prioritaria] = true)) = 12,
        "MM45_DIM_ZONA_BASE",
        "La fuente debe contener 439 zonas únicas y exactamente 12 prioritarias."
    ),
    FilaSinZona = #table(
        type table [zona_id = text, cantidad = nullable Int64.Type, heridos = nullable Int64.Type, muertos = nullable Int64.Type, cerca_100m = nullable Int64.Type, prioritaria = nullable logical],
        {{"SIN_ZONA", null, null, null, null, false}}
    ),
    Combinada = Table.Combine({ZonasBase, FilaSinZona}),
    Validada = fxControlTabla(
        Combinada,
        Table.RowCount(Combinada) = 440 and List.Count(List.Distinct(Combinada[zona_id])) = Table.RowCount(Combinada),
        "MM45_DIM_ZONA_MODELO",
        "DimZona debe añadir una única fila SIN_ZONA sin alterar las 439 zonas base."
    )
in
    Validada
