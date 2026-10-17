let
    Origen = fxCsv("powerbi/geospatial/categorias_analisis.csv"),
    Tipos = Table.TransformColumnTypes(
        Origen,
        {{"categoria_analisis", type text}, {"descripcion", type text}},
        "en-US"
    ),
    Flags = Table.TransformColumns(
        Tipos,
        {
            {"incluye_indicador_principal", each fxBool(_), type nullable logical},
            {"requiere_revision_territorial", each fxBool(_), type nullable logical}
        }
    ),
    Validada = fxControlTabla(
        Flags,
        Table.RowCount(Flags) = 5 and
            List.Count(List.Distinct(Flags[categoria_analisis])) = Table.RowCount(Flags) and
            List.NonNullCount(Flags[categoria_analisis]) = Table.RowCount(Flags),
        "MM45_DIM_CLASIFICACION",
        "DimClasificacion debe conservar cinco categorías únicas, incluida la reserva sin registros."
    )
in
    Validada
