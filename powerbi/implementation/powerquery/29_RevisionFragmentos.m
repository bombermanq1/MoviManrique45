let
    Origen = fxCsv("powerbi/geospatial/fragmentos_revision.csv"),
    Tipos = Table.TransformColumnTypes(
        Origen,
        {
            {"parte_id", type text}, {"objectid", Int64.Type}, {"parte", Int64.Type},
            {"longitud_m", type number}, {"clasificacion", type text},
            {"decision_version", type text}, {"origen_documentado", type text}
        },
        "en-US"
    ),
    Flags = Table.TransformColumns(Tipos, {{"diminuta", each fxBool(_), type nullable logical}}),
    Validada = fxControlTabla(
        Flags,
        Table.RowCount(Flags) = 6 and List.Count(List.Distinct(Flags[parte_id])) = Table.RowCount(Flags),
        "MM45_FRAGMENTOS",
        "RevisionFragmentos debe conservar las seis partes diminutas sin fusionarlas ni eliminarlas."
    )
in
    Validada
