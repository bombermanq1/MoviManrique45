# Consultas Power Query separadas — MoviManrique45

Este directorio contiene consultas **independientes y copiables** para Power BI
Desktop. Cada archivo `.m` corresponde a una sola consulta o función: cree una
consulta en blanco, asígnele exactamente el nombre indicado por el archivo
(sin el prefijo numérico) y pegue su contenido completo en el Editor avanzado.

No copie todos los archivos en una misma consulta. La carpeta reemplaza el
archivo monolítico anterior, que no podía pegarse directamente en Desktop.

## Orden de creación

1. En **Administrar parámetros**, cree `pRaiz` como parámetro de texto. Su valor
   es la carpeta raíz local del repositorio,
   credenciales ni una barra final.
2. Cree las funciones: `fxRutaProyecto`, `fxCsv`, `fxBool` y `fxControlTabla`.
   Desactive su carga.
3. Cree las consultas de preparación: `StgHechos`, `StgFechaCoordenadas` y
   `StgConFecha`. Desactive su carga.
4. Cree las dimensiones y después `FactSiniestros`.
5. Cree `ValidacionCierre` y `ControlCierreEstricto`. Manténgalas sin carga;
   ábralas y actualícelas antes de aplicar cambios. `ControlCierreEstricto`
   produce un error intencional si algún control de cierre falla.

## Consultas que se cargan al modelo

- `FactSiniestros`
- `DimFecha`
- `DimTerritorioNominal`
- `DimTerritorioGeometrico`
- `DimGravedad`
- `DimTipo`
- `DimClasificacion`
- `DimZona`
- `DimSegmento`
- `DimIdsCongelados` (ocultar del panel; se usa para controles DAX)
- `RevisionFragmentos`

`DimIdsCongelados` no tiene relación con hechos. Conserva la lista aprobada de
604/40/4 IDs solo para comparar el cierre, sin alterar ni reclasificar eventos.

## Controles que ejecutan las consultas

- 8.332 eventos únicos en los hechos.
- 604 `principal_50m`, 40 `sensibilidad_borde`, cuatro
  `revision_territorial` y 7.684 `resto_manrique`.
- Coincidencia 1:1 entre `evento_id` y `objectid`, fecha válida y
  coherencia de año/mes.
- Rango de coordenadas geográficas de la fuente auxiliar.
- Coincidencia exacta de los IDs congelados 604/40/4 contra
  `src/geospatial/ids_cierre_v1.json`.
- 26 segmentos, 439 zonas base, 12 prioritarias, 6 fragmentos y 44 eventos
  sin zona (`SIN_ZONA`) dentro del modelo.



PBIX/PBIP funcional hasta completar esa prueba manual.
      
