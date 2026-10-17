let
    Origen = fxCsv("powerbi/geospatial/hechos_siniestros.csv"),
    Tipos = Table.TransformColumnTypes(
        Origen,
        {
            {"evento_id", Int64.Type},
            {"anio", Int64.Type},
            {"mes_numero", Int64.Type},
            {"clase_siniestro", type text},
            {"gravedad_siniestro", type text},
            {"barrio", type text},
            {"num_comuna", type text},
            {"distancia_carrera45_m", type number},
            {"segmento_cercano_id", Int64.Type},
            {"zona_id", type text},
            {"categoria_analisis", type text},
            {"distancia_limite_manrique_m", type number},
            {"territorio_geometrico", type text}
        },
        "en-US"
    ),
    NombresFlags = {
        "fecha_valida", "coordenada_valida", "dentro_manrique",
        "dentro_corredor_50m", "es_indicador_principal",
        "sensibilidad_borde", "pendiente_revision_territorial"
    },
    Flags = Table.TransformColumns(
        Tipos,
        List.Transform(NombresFlags, (nombre as text) => {nombre, each fxBool(_), type nullable logical})
    ),
    FilasEsperadas = fxControlTabla(
        Flags,
        Table.RowCount(Flags) = 8332,
        "MM45_HECHOS_FILAS",
        "Se esperaban exactamente 8332 siniestros en hechos_siniestros.csv."
    ),
    IdsUnicos = fxControlTabla(
        FilasEsperadas,
        List.NonNullCount(FilasEsperadas[evento_id]) = Table.RowCount(FilasEsperadas) and
            List.Count(List.Distinct(FilasEsperadas[evento_id])) = Table.RowCount(FilasEsperadas),
        "MM45_HECHOS_IDS",
        "evento_id es nulo o duplicado; no se permite quitar filas automáticamente."
    ),
    CategoriasNoNulas = fxControlTabla(
        IdsUnicos,
        List.NonNullCount(IdsUnicos[categoria_analisis]) = Table.RowCount(IdsUnicos),
        "MM45_HECHOS_CATEGORIAS",
        "categoria_analisis contiene valores nulos."
    )
in
    CategoriasNoNulas
