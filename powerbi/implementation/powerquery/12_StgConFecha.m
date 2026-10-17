let
    Unida = Table.NestedJoin(
        StgHechos,
        {"evento_id"},
        StgFechaCoordenadas,
        {"objectid"},
        "AuxiliarFechaCoordenadas",
        JoinKind.LeftOuter
    ),
    ConCoincidencias = Table.AddColumn(
        Unida,
        "CoincidenciasAuxiliar",
        each Table.RowCount([AuxiliarFechaCoordenadas]),
        Int64.Type
    ),
    UnionUnoAUno = fxControlTabla(
        ConCoincidencias,
        List.AllTrue(List.Transform(ConCoincidencias[CoincidenciasAuxiliar], each _ = 1)),
        "MM45_UNION_1_A_1",
        "La unión evento_id/objectid no es exactamente 1:1; no se usa inner join ni se eliminan filas."
    ),
    Expandida = Table.ExpandTableColumn(
        UnionUnoAUno,
        "AuxiliarFechaCoordenadas",
        {"fecha_siniestro", "latitud", "longitud"},
        {"fecha_siniestro", "latitud", "longitud"}
    ),
    ConFechaCoherente = Table.AddColumn(
        Expandida,
        "FechaCoherente",
        each Date.Year([fecha_siniestro]) = [anio] and Date.Month([fecha_siniestro]) = [mes_numero],
        type logical
    ),
    FechasCoherentes = fxControlTabla(
        ConFechaCoherente,
        List.AllTrue(ConFechaCoherente[FechaCoherente]),
        "MM45_FECHA_PERIODO",
        "La fecha auxiliar no coincide con el año/mes validado de hechos."
    ),
    ZonaModelo = Table.AddColumn(
        FechasCoherentes,
        "zona_id_modelo",
        each if [zona_id] = null then "SIN_ZONA" else if Text.Trim([zona_id]) = "" then "SIN_ZONA" else [zona_id],
        type text
    ),
    Resultado = Table.RemoveColumns(ZonaModelo, {"AuxiliarFechaCoordenadas", "CoincidenciasAuxiliar", "FechaCoherente"})
in
    Resultado
