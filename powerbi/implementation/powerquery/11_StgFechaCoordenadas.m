let
    Origen = fxCsv("data/processed/siniestros_comuna3_limpios.csv"),
    Columnas = Table.SelectColumns(Origen, {"objectid", "fecha_siniestro", "latitud", "longitud"}),
    Tipos = Table.TransformColumnTypes(
        Columnas,
        {{"objectid", Int64.Type}, {"latitud", type number}, {"longitud", type number}},
        "en-US"
    ),
    Fechas = Table.TransformColumns(
        Tipos,
        {{"fecha_siniestro", each try Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"])
            otherwise error Error.Record("MM45_FECHA_INVALIDA", "fecha_siniestro no cumple yyyy-MM-dd.", [valor=_]), type date}}
    ),
    FilasEsperadas = fxControlTabla(
        Fechas,
        Table.RowCount(Fechas) = 8332,
        "MM45_AUX_FILAS",
        "La fuente auxiliar debe contener exactamente 8332 filas."
    ),
    IdsUnicos = fxControlTabla(
        FilasEsperadas,
        List.NonNullCount(FilasEsperadas[objectid]) = Table.RowCount(FilasEsperadas) and
            List.Count(List.Distinct(FilasEsperadas[objectid])) = Table.RowCount(FilasEsperadas),
        "MM45_AUX_IDS",
        "objectid es nulo o duplicado; no se permite una unión 1:N."
    ),
    FechasNoNulas = fxControlTabla(
        IdsUnicos,
        List.NonNullCount(IdsUnicos[fecha_siniestro]) = Table.RowCount(IdsUnicos),
        "MM45_AUX_FECHAS",
        "La fuente auxiliar contiene fechas nulas o inválidas."
    ),
    CoordenadasValidas = fxControlTabla(
        FechasNoNulas,
        List.AllTrue(List.Transform(FechasNoNulas[latitud], each if Value.Is(_, type number) then _ >= -90 and _ <= 90 else false)) and
            List.AllTrue(List.Transform(FechasNoNulas[longitud], each if Value.Is(_, type number) then _ >= -180 and _ <= 180 else false)),
        "MM45_AUX_COORDENADAS",
        "Las coordenadas auxiliares deben ser geográficas válidas; no se corrigen valores."
    )
in
    CoordenadasValidas
