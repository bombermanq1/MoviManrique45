(valor as any) as nullable logical =>
let
    Texto = if valor = null then null else Text.Lower(Text.Trim(Text.From(valor))),
    Resultado =
        if Texto = null or Texto = "" then null
        else if List.Contains({"true", "verdadero", "1"}, Texto) then true
        else if List.Contains({"false", "falso", "0"}, Texto) then false
        else error Error.Record(
            "MM45_BOOL_INVALIDO",
            "Se encontró un valor lógico no reconocido.",
            [valor=valor]
        )
in
    Resultado
