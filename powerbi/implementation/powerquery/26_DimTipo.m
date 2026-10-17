let
    Valores = Table.Distinct(Table.SelectColumns(StgConFecha, {"clase_siniestro"})),
    Ordenada = Table.Sort(Valores, {{"clase_siniestro", Order.Ascending}}),
    Validada = fxControlTabla(
        Ordenada,
        Table.RowCount(Ordenada) = 5 and List.NonNullCount(Ordenada[clase_siniestro]) = Table.RowCount(Ordenada),
        "MM45_DIM_TIPO",
        "DimTipo debe contener las cinco clases observadas sin normalizarlas ni agregarlas."
    )
in
    Validada
