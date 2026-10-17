let
    Fallos = Table.SelectRows(ValidacionCierre, each [estado] <> "OK"),
    Resultado =
        if Table.RowCount(Fallos) = 0 then
            #table(type table [resultado = text], {{"OK — cierre geoespacial y IDs congelados conciliados."}})
        else
            error Error.Record(
                "MM45_CIERRE_INVALIDO",
                "Falló al menos un control de cierre. No aplicar ni publicar el modelo.",
                Fallos
            )
in
    Resultado
