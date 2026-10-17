(rutaRelativa as text) as table =>
let
    Ruta = fxRutaProyecto(rutaRelativa),
    Fuente = Csv.Document(
        File.Contents(Ruta),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Cabeceras = Table.PromoteHeaders(Fuente, [PromoteAllScalars=true])
in
    Cabeceras
