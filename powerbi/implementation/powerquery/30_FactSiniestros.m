let
    UnidaTerritorio = Table.NestedJoin(
        StgConFecha,
        {"num_comuna", "barrio"},
        DimTerritorioNominal,
        {"num_comuna", "barrio"},
        "DimensionTerritorio",
        JoinKind.LeftOuter
    ),
    ConCoincidencias = Table.AddColumn(
        UnidaTerritorio,
        "CoincidenciasTerritorio",
        each Table.RowCount([DimensionTerritorio]),
        Int64.Type
    ),
    UnionUnoAUno = fxControlTabla(
        ConCoincidencias,
        Table.RowCount(ConCoincidencias) = 8332 and
            List.AllTrue(List.Transform(ConCoincidencias[CoincidenciasTerritorio], each _ = 1)),
        "MM45_HECHOS_TERRITORIO",
        "Cada siniestro debe coincidir con exactamente un territorio nominal."
    ),
    Expandida = Table.ExpandTableColumn(
        UnionUnoAUno,
        "DimensionTerritorio",
        {"TerritorioId"},
        {"TerritorioId"}
    ),
    Resultado = Table.RemoveColumns(Expandida, {"CoincidenciasTerritorio", "DimensionTerritorio"})
in
    Resultado
