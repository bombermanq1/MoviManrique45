let
    Valores = Table.Distinct(Table.SelectColumns(StgConFecha, {"gravedad_siniestro"})),
    Ordenada = Table.Sort(Valores, {{"gravedad_siniestro", Order.Ascending}}),
    Validada = fxControlTabla(
        Ordenada,
        Table.RowCount(Ordenada) = 2 and List.NonNullCount(Ordenada[gravedad_siniestro]) = Table.RowCount(Ordenada),
        "MM45_DIM_GRAVEDAD",
        "DimGravedad debe contener los dos valores observados sin inventar categorías."
    )
in
    Validada
