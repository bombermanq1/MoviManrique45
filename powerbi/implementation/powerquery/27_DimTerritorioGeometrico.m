let
    Valores = Table.Distinct(Table.SelectColumns(StgConFecha, {"territorio_geometrico"})),
    Renombrada = Table.RenameColumns(Valores, {{"territorio_geometrico", "TerritorioGeometrico"}}),
    Ordenada = Table.Sort(Renombrada, {{"TerritorioGeometrico", Order.Ascending}}),
    Validada = fxControlTabla(
        Ordenada,
        Table.RowCount(Ordenada) = 4 and List.NonNullCount(Ordenada[TerritorioGeometrico]) = Table.RowCount(Ordenada),
        "MM45_DIM_TERRITORIO_GEOMETRICO",
        "DimTerritorioGeometrico debe contener los cuatro territorios geométricos observados."
    )
in
    Validada
