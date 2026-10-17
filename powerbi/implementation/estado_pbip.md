# Estado PBIX/PBIP y bloqueo de validación

**Estado actual: BLOQUEADO para generar un archivo PBIX/PBIP válido y probado.**

La revisión estática confirma que el repositorio no contiene archivos `.pbix`,
`.pbip` ni `.pbit`. Un PBIP no es solamente un conjunto de archivos de texto:
el modelo, las consultas, el reporte, los visuales y la versión de esquema deben
abrirse, actualizarse y renderizarse correctamente en Power BI Desktop.

En esta ejecución no hay una superficie de automatización confiable para la
ventana nativa de Power BI Desktop. Generar de forma manual un PBIP desde texto
sin abrirlo no permitiría comprobar:

- compatibilidad de los esquemas del modelo y del reporte;
- ejecución de Power Query y DAX;
- relaciones activas y dirección de filtro;
- disponibilidad de los visuales de mapa y referencias GeoJSON;
- refresh, guardado y reapertura del archivo.

Por esa razón no se fabrica un PBIX/PBIP que podría ser inválido. El bloqueo no
afecta los recursos manuales: las consultas separadas, modelo, medidas, guía de
cuatro páginas y controles de cierre están preparados en esta carpeta.

## Procedimiento cuando Power BI Desktop esté disponible

1. Trabaje inicialmente en una ruta local corta no sincronizada por OneDrive.
2. Cree un reporte nuevo y defina el parámetro `pRaiz` con la raíz del proyecto.
3. Pegue las consultas de `powerquery/` en el orden documentado y actualice
   `ControlCierreEstricto` hasta que no produzca error.
4. Cargue las tablas indicadas, cree las relaciones de `modelo_relaciones.md` y
   compile cada medida de `dax/medidas_modelo.dax`.
5. Construya y pruebe las cuatro páginas siguiendo `guia_4_paginas.md`.
6. Compruebe sin filtros 8.332/604/40/4/7.684 y la integridad exacta de 604 IDs.
7. Guarde como **Power BI Project (.pbip)** o PBIX, cierre, reabra y actualice.
8. Solo después de esas pruebas copie el artefacto validado al repositorio y
   registre versión de Desktop, fecha y resultado de refresh.

No conecte PostgreSQL, no publique ni modifique datasets geoespaciales durante
este procedimiento.
