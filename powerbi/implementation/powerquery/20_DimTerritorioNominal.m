let
    Pares = Table.Distinct(Table.SelectColumns(StgConFecha, {"num_comuna", "barrio"})),
    Ordenados = Table.Sort(Pares, {{"num_comuna", Order.Ascending}, {"barrio", Order.Ascending}}),
    ConClave = Table.AddIndexColumn(Ordenados, "TerritorioId", 1, 1, Int64.Type),
    Validada = fxControlTabla(
        ConClave,
        Table.RowCount(ConClave) = 18 and List.Count(List.Distinct(ConClave[TerritorioId])) = Table.RowCount(ConClave),
        "MM45_DIM_TERRITORIO",
        "DimTerritorioNominal debe tener 18 pares únicos comuna/barrio."
    )
in
    Validada
