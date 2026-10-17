(rutaRelativa as text) as text =>
let
    Separador = Character.FromNumber(92),
    Base = Text.TrimEnd(Text.Replace(Text.Trim(pRaiz), "/", Separador), Separador),
    Relativa = Text.TrimStart(Text.Replace(Text.Trim(rutaRelativa), "/", Separador), Separador),
    Resultado = Base & Separador & Relativa
in
    Resultado
