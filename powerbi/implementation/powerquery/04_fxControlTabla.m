(tabla as table, condicion as logical, codigo as text, mensaje as text) as table =>
    if condicion then
        tabla
    else
        error Error.Record(codigo, mensaje)
