/*
Índice válido para Power Query.

No contiene varias consultas concatenadas. Cree una consulta en blanco llamada
IndicePowerQuery y pegue este archivo si desea ver la lista de recursos.
Para construir el modelo, use los archivos separados de powerquery/README.md
en el orden indicado allí.
*/
let
    Recursos = #table(
        type table [orden = Int64.Type, consulta = text, archivo = text, cargar_al_modelo = text],
        {
            {1, "pRaiz", "powerquery/00_parametro_pRaiz.m.template", "Parámetro"},
            {2, "fxRutaProyecto", "powerquery/01_fxRutaProyecto.m", "No"},
            {3, "fxCsv", "powerquery/02_fxCsv.m", "No"},
            {4, "fxBool", "powerquery/03_fxBool.m", "No"},
            {5, "fxControlTabla", "powerquery/04_fxControlTabla.m", "No"},
            {10, "StgHechos", "powerquery/10_StgHechos.m", "No"},
            {11, "StgFechaCoordenadas", "powerquery/11_StgFechaCoordenadas.m", "No"},
            {12, "StgConFecha", "powerquery/12_StgConFecha.m", "No"},
            {20, "DimTerritorioNominal", "powerquery/20_DimTerritorioNominal.m", "Sí"},
            {21, "DimFecha", "powerquery/21_DimFecha.m", "Sí"},
            {22, "DimClasificacion", "powerquery/22_DimClasificacion.m", "Sí"},
            {23, "DimSegmento", "powerquery/23_DimSegmento.m", "Sí"},
            {24, "DimZona", "powerquery/24_DimZona.m", "Sí"},
            {25, "DimGravedad", "powerquery/25_DimGravedad.m", "Sí"},
            {26, "DimTipo", "powerquery/26_DimTipo.m", "Sí"},
            {27, "DimTerritorioGeometrico", "powerquery/27_DimTerritorioGeometrico.m", "Sí"},
            {28, "DimIdsCongelados", "powerquery/28_DimIdsCongelados.m", "Sí (oculta)"},
            {29, "RevisionFragmentos", "powerquery/29_RevisionFragmentos.m", "Sí"},
            {30, "FactSiniestros", "powerquery/30_FactSiniestros.m", "Sí"},
            {40, "ValidacionCierre", "powerquery/40_ValidacionCierre.m", "No"},
            {41, "ControlCierreEstricto", "powerquery/41_ControlCierreEstricto.m", "No"}
        }
    )
in
    Recursos
