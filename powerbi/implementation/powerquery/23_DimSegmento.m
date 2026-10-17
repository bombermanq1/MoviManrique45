let
    Origen = fxCsv("powerbi/geospatial/segmentos.csv"),
    Tipos = Table.TransformColumnTypes(
        Origen,
        {{"segmento_cercano_id", Int64.Type}, {"longitud_m", type number}},
        "en-US"
    ),
    Flags = Table.TransformColumns(
        Tipos,
        {{"valida", each fxBool(_), type nullable logical}, {"duplicada", each fxBool(_), type nullable logical}}
    ),
    Validada = fxControlTabla(
        Flags,
        Table.RowCount(Flags) = 26 and List.Count(List.Distinct(Flags[segmento_cercano_id])) = Table.RowCount(Flags),
        "MM45_DIM_SEGMENTO",
        "DimSegmento debe conservar 26 segmentos únicos."
    )
in
    Validada
