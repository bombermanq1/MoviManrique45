let
    SonIguales = (esperados as list, observados as list) as logical =>
        List.Count(List.Difference(esperados, observados)) = 0 and
            List.Count(List.Difference(observados, esperados)) = 0,
    FilasHechos = Table.RowCount(FactSiniestros),
    Principal = Table.SelectRows(FactSiniestros, each [categoria_analisis] = "principal_50m"),
    Sensibilidad = Table.SelectRows(FactSiniestros, each [categoria_analisis] = "sensibilidad_borde"),
    Revision = Table.SelectRows(FactSiniestros, each [categoria_analisis] = "revision_territorial"),
    Resto = Table.SelectRows(FactSiniestros, each [categoria_analisis] = "resto_manrique"),
    IdsEsperadosPrincipal = List.Sort(Table.SelectRows(DimIdsCongelados, each [categoria_analisis] = "principal_50m")[evento_id]),
    IdsEsperadosSensibilidad = List.Sort(Table.SelectRows(DimIdsCongelados, each [categoria_analisis] = "sensibilidad_borde")[evento_id]),
    IdsEsperadosRevision = List.Sort(Table.SelectRows(DimIdsCongelados, each [categoria_analisis] = "revision_territorial")[evento_id]),
    IdsActualesPrincipal = List.Sort(Principal[evento_id]),
    IdsActualesSensibilidad = List.Sort(Sensibilidad[evento_id]),
    IdsActualesRevision = List.Sort(Revision[evento_id]),
    SinZona = Table.RowCount(Table.SelectRows(FactSiniestros, each [zona_id_modelo] = "SIN_ZONA")),
    ZonasBase = Table.RowCount(Table.SelectRows(DimZona, each [zona_id] <> "SIN_ZONA")),
    ZonasPrioritarias = Table.RowCount(Table.SelectRows(DimZona, each [prioritaria] = true)),
    Controles = #table(
        type table [control = text, esperado = text, observado = text, estado = text],
        {
            {"Filas FactSiniestros", "8332", Text.From(FilasHechos), if FilasHechos = 8332 then "OK" else "ERROR"},
            {"IDs únicos de hechos", "8332", Text.From(List.Count(List.Distinct(FactSiniestros[evento_id]))), if List.Count(List.Distinct(FactSiniestros[evento_id])) = 8332 then "OK" else "ERROR"},
            {"principal_50m", "604", Text.From(Table.RowCount(Principal)), if Table.RowCount(Principal) = 604 then "OK" else "ERROR"},
            {"IDs congelados principal exactos", "604 IDs", Text.From(List.Count(IdsActualesPrincipal)) & " IDs", if SonIguales(IdsEsperadosPrincipal, IdsActualesPrincipal) then "OK" else "ERROR"},
            {"sensibilidad_borde", "40", Text.From(Table.RowCount(Sensibilidad)), if Table.RowCount(Sensibilidad) = 40 then "OK" else "ERROR"},
            {"IDs congelados sensibilidad exactos", "40 IDs", Text.From(List.Count(IdsActualesSensibilidad)) & " IDs", if SonIguales(IdsEsperadosSensibilidad, IdsActualesSensibilidad) then "OK" else "ERROR"},
            {"revision_territorial", "4", Text.From(Table.RowCount(Revision)), if Table.RowCount(Revision) = 4 then "OK" else "ERROR"},
            {"IDs congelados revisión exactos", "4 IDs", Text.From(List.Count(IdsActualesRevision)) & " IDs", if SonIguales(IdsEsperadosRevision, IdsActualesRevision) then "OK" else "ERROR"},
            {"resto_manrique", "7684", Text.From(Table.RowCount(Resto)), if Table.RowCount(Resto) = 7684 then "OK" else "ERROR"},
            {"Segmentos", "26", Text.From(Table.RowCount(DimSegmento)), if Table.RowCount(DimSegmento) = 26 then "OK" else "ERROR"},
            {"Zonas base", "439", Text.From(ZonasBase), if ZonasBase = 439 then "OK" else "ERROR"},
            {"Zonas prioritarias", "12", Text.From(ZonasPrioritarias), if ZonasPrioritarias = 12 then "OK" else "ERROR"},
            {"Fragmentos conservados", "6", Text.From(Table.RowCount(RevisionFragmentos)), if Table.RowCount(RevisionFragmentos) = 6 then "OK" else "ERROR"},
            {"Eventos SIN_ZONA", "44", Text.From(SinZona), if SinZona = 44 then "OK" else "ERROR"}
        }
    )
in
    Controles
