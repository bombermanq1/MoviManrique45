# Validación estática de recursos Power BI

Resultado: **24/25 controles OK**; 0 error(es) y 1 bloqueo(s).

Esta ejecución leyó fuentes locales y escribió únicamente este informe y su JSON asociado. No abre ni controla Power BI Desktop; por tanto, no certifica la compilación de M/DAX, relaciones, render o refresh en Desktop.

| Control | Estado | Detalle |
|---|---|---|
| Hechos: filas e IDs únicos | OK | filas=8332, IDs únicos=8332 |
| Clasificación excluyente | OK | conteos={'resto_manrique': 7684, 'principal_50m': 604, 'sensibilidad_borde': 40, 'revision_territorial': 4} |
| IDs congelados exactos: principal_50m | OK | esperados=604, observados=604 |
| IDs congelados exactos: sensibilidad_borde | OK | esperados=40, observados=40 |
| IDs congelados exactos: revision_territorial | OK | esperados=4, observados=4 |
| Unión auxiliar 1:1 | OK | hechos=8332, auxiliar=8332, fechas sin coincidencia=0 |
| Fecha y coordenadas auxiliares | OK | fechas inválidas=0, periodos coherentes=True, coordenadas en rango=True |
| Segmentos | OK | filas=26, IDs únicos=26 |
| Partes geométricas | OK | capa=partes, filas=33, partes únicas=33, CRS=EPSG:9377 |
| Fragmentos conservados | OK | filas=6, partes únicas=6 |
| Zonas de concentración | OK | zonas=439, prioritarias=12 |
| Eventos sin zona | OK | sin zona=44 |
| Consultas M separadas | OK | todas presentes |
| Consultas M sin fuentes prohibidas | OK | sin PostgreSQL/SQL/API |
| Estructura léxica de consultas M | OK | paréntesis, llaves, corchetes y estructura let/in o función revisados; no sustituye Power BI Desktop |
| Contenido M: 10_StgHechos.m | OK | términos verificados=['8332', 'evento_id'] |
| Contenido M: 12_StgConFecha.m | OK | términos verificados=['JoinKind.LeftOuter', 'CoincidenciasAuxiliar', 'zona_id_modelo'] |
| Contenido M: 28_DimIdsCongelados.m | OK | términos verificados=['ids_cierre_v1.json', '604'] |
| Contenido M: 40_ValidacionCierre.m | OK | términos verificados=['IDs congelados principal exactos', '7684'] |
| Contenido M: 41_ControlCierreEstricto.m | OK | términos verificados=['MM45_CIERRE_INVALIDO'] |
| Medidas DAX requeridas | OK | medidas esperadas=21; faltantes=[] |
| Paréntesis DAX balanceados | OK | comprobación estática; no reemplaza la compilación en Desktop |
| DAX con control de 604 IDs | OK | medida de comparación exacta presente |
| PBIX/PBIP/PBIT | BLOQUEADO | No existe un archivo Power BI real en el repositorio; el bloqueo queda documentado. |
| Fuentes protegidas sin escritura | OK | hashes iguales antes/después de la validación |

## Estado PBIP/PBIX

BLOQUEADO: no se genera PBIP/PBIX sin apertura, refresh y validación en Power BI Desktop.

Los recursos manuales se encuentran en `powerquery/`, `dax/`, `modelo_relaciones.md` y `guia_4_paginas.md`.
