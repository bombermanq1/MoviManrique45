let
    Inicio = Date.StartOfYear(List.Min(StgConFecha[fecha_siniestro])),
    Fin = Date.EndOfYear(List.Max(StgConFecha[fecha_siniestro])),
    Lista = List.Dates(Inicio, Duration.Days(Fin - Inicio) + 1, #duration(1, 0, 0, 0)),
    Base = Table.FromList(Lista, Splitter.SplitByNothing(), {"Fecha"}, null, ExtraValues.Error),
    Tipada = Table.TransformColumnTypes(Base, {{"Fecha", type date}}),
    Anio = Table.AddColumn(Tipada, "Año", each Date.Year([Fecha]), Int64.Type),
    MesNumero = Table.AddColumn(Anio, "MesNumero", each Date.Month([Fecha]), Int64.Type),
    Mes = Table.AddColumn(MesNumero, "Mes", each Date.MonthName([Fecha], "es-CO"), type text),
    AnioMes = Table.AddColumn(Mes, "AñoMes", each Date.ToText([Fecha], "yyyy-MM"), type text),
    OrdenAnioMes = Table.AddColumn(AnioMes, "OrdenAñoMes", each [Año] * 100 + [MesNumero], Int64.Type),
    TrimestreNumero = Table.AddColumn(OrdenAnioMes, "TrimestreNumero", each Date.QuarterOfYear([Fecha]), Int64.Type),
    Trimestre = Table.AddColumn(TrimestreNumero, "Trimestre", each "T" & Text.From([TrimestreNumero]), type text),
    Validada = fxControlTabla(
        Trimestre,
        Table.RowCount(Trimestre) = 2557 and List.Count(List.Distinct(Trimestre[Fecha])) = Table.RowCount(Trimestre),
        "MM45_DIM_FECHA",
        "DimFecha debe contener 2557 días únicos de 2019-01-01 a 2025-12-31."
    )
in
    Validada
