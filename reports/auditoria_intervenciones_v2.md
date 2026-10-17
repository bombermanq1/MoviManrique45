# Auditoría de cierre v2 — módulo de intervenciones

**Fecha:** 16 de octubre de 2026  
**Raíz auditada:** `C:\Users\matth\OneDrive\Escritorio\ITM\movimanrique45`  
**Alcance:** módulo web de intervenciones exploratorias, rediseño web, entregables v2 y pruebas no destructivas.

## Veredicto

| Componente | Estado | Evidencia verificable |
|---|---|---|
| Datos y cierre geoespacial | COMPLETADO | Suite y controles conservan 8.332 / 604 / 40 / 4 / 7.684, 26 segmentos, 33 partes, 6 fragmentos, 439 celdas y 12 zonas. |
| Módulo de intervenciones | COMPLETADO | `web/data/intervenciones.json`, `src/dashboard/intervenciones.py` y seis pruebas dedicadas. |
| Dashboard y geovisor web | COMPLETADO | Contrato HTML, JSON servidos por HTTP local y pruebas de exportación y capas. |
| Diseño responsive | PARCIAL | CSS responsive y revisión estática completados. No se hizo una nueva interacción manual en navegador durante este cierre. |
| Documentos v2 | COMPLETADO | Cuatro DOCX y cuatro PDF nuevos; revisión visual de sus ocho páginas renderizadas. |
| Presentación v2 | COMPLETADO | PPTX nuevo de 10 diapositivas, validación estructural y revisión visual de cada diapositiva. |
| Power BI Desktop | PARCIAL | Continúan recursos estáticos; no existe PBIX/PBIP validado. |
| ML/IA predictiva | NO IMPLEMENTADO | El proyecto conserva análisis GIS exploratorio y no declara un modelo predictivo. |

## Integridad comprobada

La suite aprobada comprobó la partición excluyente de los siniestros, la identidad
congelada de los conjuntos, CRS, capas y geometrías. El resultado vigente es:

| Indicador | Valor |
|---|---:|
| Siniestros de Comuna 3 | 8.332 |
| Corredor territorial estricto | 604 |
| Sensibilidad de borde | 40 |
| Revisión territorial | 4 |
| Resto de Manrique | 7.684 |
| Eje de Carrera 45 | 26 segmentos; 1.698,67 m |
| Partes / fragmentos menores de 1 m | 33 / 6 |
| Celdas / zonas exploratorias | 439 / 12 |

El módulo no crea zonas nuevas ni modifica la capa de zonas. Cada ficha se deriva
de los eventos web con el mismo `zona_id`, conserva tipos, gravedad y categorías
observadas, y calcula los segmentos reportados con intersecciones geométricas
contra el eje exportado.

## Reglas de intervención verificadas

- Las 12 fichas inician en `Pendiente de inspección`.
- El catálogo incluye ocho medidas candidatas: pasos peatonales, reductores de
  velocidad, señalización, accesibilidad universal, rampas y cruces, control de
  velocidad, protección peatonal y visibilidad del espacio peatonal.
- Cada ficha declara que requiere inspección de campo y evaluación técnica.
- Los costos por zona permanecen en `Pendiente de estudio técnico y presupuesto`.
- El orden comparativo usa solamente el recuento histórico de registros de la
  celda. No representa riesgo, causalidad ni prioridad oficial.

## Pruebas ejecutadas

| Comprobación | Resultado |
|---|---|
| Compilación Python | `python -m compileall -q src app.py tests` sin errores |
| Suite automatizada | `python -m unittest discover -s tests -v`: **50/50 aprobadas** en 2,884 s |
| HTTP local en prueba | Página, `dashboard.json` e `intervenciones.json` respondieron HTTP 200 |
| Integridad oficial | Pruebas de fuente, IDs, geometrías, fragmentos y cierre aprobadas |
| Intervenciones | Seis pruebas: 12 zonas, métricas, catálogo, costos, intersecciones y HTML |
| Presentación | 10 diapositivas, dos tablas nativas y un gráfico nativo validados estructuralmente |
| Documentos | Técnico: 5 páginas; resumen, presupuesto y manual: 1 página cada uno |

La política del navegador de la sesión impidió abrir una nueva sesión manual de
UI durante este cierre. Por eso esta auditoría no declara una nueva prueba manual
de filtros, arrastre o móvil. Las funciones se cubren por pruebas de contrato,
exportación y HTTP; la prueba manual previa del MVP se conserva separada en la
auditoría anterior.

## Archivos generados y revisados

- `deliverables/final/v2/MoviManrique45_Documento_Tecnico_v2_Intervenciones.docx`
  y su PDF.
- `deliverables/final/v2/MoviManrique45_Resumen_Ejecutivo_v2_Intervenciones.docx`
  y su PDF.
- `deliverables/final/v2/MoviManrique45_Presupuesto_Seis_Meses_v2_Intervenciones.docx`
  y su PDF.
- `deliverables/final/v2/MoviManrique45_Manual_Demostracion_v2_Intervenciones.docx`
  y su PDF.
- `deliverables/final/v2/MoviManrique45_Presentacion_v2_Intervenciones.pptx`.

## Limitaciones y acciones posteriores

1. Una inspección de campo debe validar velocidades, visibilidad, cruces,
   accesibilidad, flujos y conflictos antes de plantear obra física.
2. No hay costos de obra por zona porque faltan cantidades, diseños, permisos y
   precios unitarios verificables.
3. Power BI sigue pendiente de un archivo nativo validado en Desktop.
4. No existe ML predictivo y no debe presentarse el análisis exploratorio como IA
   operativa.
5. La próxima demostración manual debe comprobar filtros, arrastre del mapa,
   selección de una zona y la vista móvil en el navegador local.

## Salvaguardas aplicadas

No se modificaron archivos RAW, datasets oficiales procesados, geometrías,
IDs congelados, PostgreSQL ni el repositorio externo. No se realizaron commits,
pushes ni despliegues públicos.
