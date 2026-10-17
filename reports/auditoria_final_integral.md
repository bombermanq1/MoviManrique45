# Auditoría final integral — MoviManrique45

**Fecha:** 16 de octubre de 2026  
**Raíz auditada:** `C:\Users\matth\OneDrive\Escritorio\ITM\movimanrique45`  
**Método:** comprobación directa de capas derivadas, ejecución de pruebas no destructivas, navegación local del dashboard, validación estructural de documentos y revisión estática de seguridad. Esta auditoría no modificó fuentes RAW, datasets validados ni PostgreSQL.

## Resultado ejecutivo

El **MVP web está listo para demostrarse localmente**. La ejecución real de `scripts/iniciar_demo.ps1` verificó los insumos del cierre `v1`, exportó la vista derivada de 8.332 eventos y sirvió el dashboard exclusivamente en `127.0.0.1:8501`. En navegador se verificaron indicadores, filtros, gráficos, capas y consulta de zonas con datos reales.

El alcance completo no está terminado: no existe un PBIX/PBIP/PBIT real validado en Power BI Desktop. No existe aprendizaje automático predictivo; el proyecto documenta correctamente el análisis exploratorio GIS sin presentarlo como IA funcional. Esas limitaciones no invalidan el MVP web, pero impiden declarar completado el 100 % del alcance ampliado.

## Evidencia de integridad de datos

| Indicador comprobado sobre datos | Resultado |
|---|---:|
| Siniestros analizados e IDs únicos | 8.332 / 8.332 |
| Corredor estricto / borde / revisión / resto | 604 / 40 / 4 / 7.684 |
| Dentro / fuera del límite geométrico | 8.288 / 44 |
| Proximidad simple al eje `<= 50 m` | 644 |
| Segmentos / partes / fragmentos `< 1 m` | 26 / 33 / 6 |
| Celdas de concentración / zonas prioritarias | 439 / 12 |
| Geometrías inválidas, siniestros / segmentos | 0 / 0 |
| CRS de capas procesadas | EPSG:9377 |
| Coincidencia con `ids_cierre_v1.json` | Exacta para principal, borde y revisión |

La comprobación leyó `data/processed/geospatial/siniestros_analisis.gpkg`, `carrera45_auditoria.gpkg` y `src/geospatial/ids_cierre_v1.json`. Los 644 casos de proximidad simple permanecen explícitamente separados del indicador territorial estricto de 604.

## Pruebas y verificaciones ejecutadas

| Comprobación | Resultado verificable |
|---|---|
| Suite Python | Cierre anterior: `44/44`; actualización v2: `50/50` aprobadas, `0` fallos, `2,884 s` |
| Insumos de demostración | `scripts/verificar_insumos_demo.py`: hashes SHA-256 correctos |
| Iniciador real | Verificó insumos, exportó 8.332 eventos y abrió `http://127.0.0.1:8501/` |
| Red local | Listener comprobado en `127.0.0.1:8501`, no en todas las interfaces |
| Cierre de prueba local | Servidores temporales detenidos; al finalizar, listeners en el puerto `8501`: `0` |
| Dashboard en navegador | Indicadores 8.332 / 604 / 40 / 4 visibles; sin errores de consola |
| Filtros en navegador | 2025: 1.145; + Manrique Central No.2: 118; + principal: 16; restablecer: 8.332 |
| Geovisor en navegador | Capas probadas; activar resto muestra 8.332; zona `47173_22505` devuelve 64 registros exploratorios |
| Power BI estático | `24` controles aprobados, `0` errores, `1` bloqueo de PBIX/Desktop |
| Dependencias y sintaxis | `pip check` sin requisitos rotos; `compileall` correcto |
| Documentos finales | Cuatro DOCX ZIP válidos; PDFs: técnico 5 páginas y los otros tres 1 página; PPTX ZIP válido de 10 diapositivas |
| Secretos | Búsqueda estática sin literales de credenciales; referencias PostgreSQL usan entorno/prompt |

## Matriz de cumplimiento reconstruida (38 requisitos)

No se encontró en el repositorio la matriz histórica con sus 38 filas. Los porcentajes previos sí permiten confirmar el denominador: `31/38 = 81,6 %` y `18/38 = 47,4 %`. Para no inventar esa matriz, las 38 filas siguientes normalizan de forma trazable los requisitos de los prompts. La comparación de porcentajes es numérica, no una equivalencia histórica fila por fila.

| # | Requisito | Estado | Evidencia | Límite pendiente |
|---:|---|---|---|---|
| 1 | Universo de 8.332; 8.288 dentro y 44 fuera | COMPLETADO | Recuento directo de GeoPackage | — |
| 2 | Corredor territorial estricto de 604 | COMPLETADO | Campo y categoría de cierre | — |
| 3 | Igualdad exacta de los 604 IDs congelados | COMPLETADO | Comparación de conjuntos aprobada | — |
| 4 | Separar 604 estrictos de 644 por proximidad | COMPLETADO | Recuento directo y textos de limitación | — |
| 5 | 40 de borde, 4 de revisión y 7.684 restantes | COMPLETADO | Partición exclusiva comprobada | — |
| 6 | 26 segmentos y 33 partes geométricas | COMPLETADO | `carrera45_auditoria.gpkg` | — |
| 7 | Seis fragmentos menores de un metro conservados | COMPLETADO | Capa de fragmentos y pruebas | — |
| 8 | 439 celdas de concentración | COMPLETADO | Capa de concentraciones | — |
| 9 | 12 zonas prioritarias exploratorias | COMPLETADO | Capa y contrato web | — |
| 10 | Calidad: claves, nulos, duplicados y categorías | COMPLETADO | IDs únicos, geometrías válidas y pruebas | — |
| 11 | Dashboard ejecutable en navegador | COMPLETADO | Iniciador real y navegador local | — |
| 12 | Dashboard conectado a datos y KPIs reales | COMPLETADO | Exportador y conciliación de conteos | — |
| 13 | Filtros por año, barrio y categoría | COMPLETADO | Prueba interactiva con cambios de conteo | — |
| 14 | Gráficos temporal, gravedad y tipo | COMPLETADO | Renderizado en navegador con datos reales | — |
| 15 | Mapa con límite, eje, zonas y categorías | COMPLETADO | Capas visibles y consistentes | — |
| 16 | Metodología, calidad y limitaciones visibles | COMPLETADO | Secciones accesibles en la UI | — |
| 17 | Geovisor operativo | COMPLETADO | 648 puntos iniciales y datos oficiales | — |
| 18 | Zoom y desplazamiento | PARCIAL | Zoom verificado; handlers de arrastre existen | Falta comprobación manual independiente de arrastre/Ajustar vista |
| 19 | Alternar capas del geovisor | COMPLETADO | Cambio de capa comprobado en navegador | — |
| 20 | Consulta contextual de zonas | COMPLETADO | Zona 47173_22505: 64 registros exploratorios | — |
| 21 | Segmentos, categorías y leyenda | COMPLETADO | Leyenda y controles en la UI | — |
| 22 | PBIX/PBIP/PBIT válido y abrible | BLOQUEADO | No existe archivo nativo de Power BI | Requiere creación y prueba en Desktop |
| 23 | Modelo y consultas Power Query | PARCIAL | Archivos M, relaciones y validador estático | Falta carga/refresh nativo |
| 24 | Medidas DAX funcionales | PARCIAL | Medidas DAX preparadas | Falta compilación y evaluación en Desktop |
| 25 | Fecha y coordenadas por ID en Power BI | PARCIAL | Consultas de staging preparadas | Falta refresh nativo |
| 26 | Relaciones PBI sin duplicaciones | PARCIAL | Modelo y validaciones estáticas | Falta prueba del modelo vivo |
| 27 | Cuatro páginas de Power BI | PARCIAL | Guía de páginas y recursos | No hay páginas materializadas |
| 28 | Interacciones Power BI y coherencia 604 | BLOQUEADO | Sin PBIX/PBIP ni Desktop | No verificable hasta implementarlo |
| 29 | Documento técnico ≤5 páginas, DOCX/PDF | COMPLETADO | DOCX válido y PDF de 5 páginas | — |
| 30 | Resumen ejecutivo ≤1 página, DOCX/PDF | COMPLETADO | DOCX válido y PDF de 1 página | — |
| 31 | Presupuesto COP 300.300.000 con desglose | PARCIAL | PDF/DOCX válidos y total correcto | Servicios/infraestructura están agrupados; obra física sin cuantificar |
| 32 | Presentación PPTX de ~10 diapositivas | COMPLETADO | PPTX válido, 10 diapositivas | — |
| 33 | Manual y reproducibilidad desde un checkout limpio | PARCIAL | Manual, manifiesto SHA-256, preflight y un comando | Los datos excluidos de Git deben recibirse por canal interno; no se distribuye un paquete de datos |
| 34 | Informe de pruebas actualizado | COMPLETADO | `deliverables/informe_validacion_mvp.md`: 50/50; actualización v2 registrada | — |
| 35 | IA/ML evaluada y estado honesto | COMPLETADO | `reports/ia_exploratoria.md` distingue GIS descriptivo de ML | No hay ML predictivo, correctamente declarado |
| 36 | Recomendaciones territoriales preliminares | COMPLETADO | Recomendaciones de seguridad, accesibilidad, señalización y velocidad | Requieren validación de campo/autoridad |
| 37 | Seguridad, integridad y disciplina Git | PARCIAL | `.gitignore`, hashes, escaneo y pruebas de fuente | No puede probarse la historia total de Git/pushes previa a la auditoría |
| 38 | Pruebas ejecutadas sobre componentes | COMPLETADO | Suite de 44, navegador y validaciones estructurales | PBI y Streamlit opcional no se ejecutaron de extremo a extremo |

## Porcentajes

- **Implementación comprobable: 36/38 = 94,7 %.** Incluye COMPLETADO y PARCIAL con evidencia tangible.
- **Cumplimiento totalmente verificado: 27/38 = 71,1 %.** Cuenta solo COMPLETADO.
- Frente a los porcentajes reportados antes (81,6 % y 47,4 %), la variación numérica es **+13,1** y **+23,7 puntos porcentuales**. No se afirma una comparación estricta de filas porque no está disponible la matriz histórica.

## Hallazgos y plan de cierre

| Prioridad | Acción | Motivo |
|---|---|---|
| P1 | Crear y validar un PBIX/PBIP real en Power BI Desktop | Es el principal bloque funcional no materializado |
| P2 | Separar servicios tecnológicos e infraestructura en el presupuesto, sin alterar el total sin justificación | Completa el desglose solicitado |
| P2 | Probar manualmente el arrastre y Ajustar vista del geovisor | Cierra la verificación específica de interacción |
| P2 | Entregar internamente el paquete de datos con el manifiesto | Permite repetir la demo desde un checkout limpio sin publicar datos |
| P2 | Revisar/stagear archivos nuevos y crear commit solo con autorización | Mantiene trazabilidad sin incumplir la restricción Git |
| P3 | Evaluar ML solo con objetivo, exposición, partición temporal y métrica válidos | Evita una predicción sin sustento |

## Veredicto explícito

1. **¿Está terminado?** El MVP demostrable sí; el alcance completo no.
2. **¿Funciona el dashboard?** Sí, probado localmente en navegador con datos reales.
3. **¿Funciona el geovisor?** Sí para capas, consulta de zonas y zoom; queda una comprobación menor de arrastre/Ajustar vista.
4. **¿Power BI está implementado?** No; está diseñado y preparado estáticamente, sin PBIX/PBIP validado.
5. **¿Existe IA funcional?** No; existe análisis exploratorio GIS correctamente documentado.
6. **¿Los datos oficiales están preservados?** Sí según hashes, comprobaciones directas y pruebas ejecutadas; no se afirma una prueba histórica absoluta anterior a la auditoría.
7. **¿Los documentos están completos?** Los archivos finales existen, abren y respetan los límites de páginas; el presupuesto conserva un desglose pendiente menor.
8. **¿Puede demostrarse hoy?** Sí, localmente con el dashboard web.
9. **¿Qué falta para 100 %?** PBIX/PBIP/validación Desktop, detalles de presupuesto, paquete interno de datos, verificación menor del geovisor y, solo si es válido, ML.
10. **¿Riesgo principal?** Presentar recursos estáticos de Power BI como producto Power BI operativo o convertir un criterio espacial de 604 eventos en una afirmación de causalidad/riesgo.

## Ejecución segura de la demostración

```powershell
.\.venv\Scripts\python.exe .\scripts\verificar_insumos_demo.py
.\scripts\iniciar_demo.ps1
```

Abra `http://127.0.0.1:8501/`. El iniciador verifica los hashes de los insumos locales, valida el cierre y queda limitado a loopback. Los datos no se publican ni se copian al repositorio.

## Actualización v2: intervenciones exploratorias

La actualización posterior incorporó doce fichas de intervención con evidencia
histórica conciliada, ocho medidas candidatas y estado inicial `Pendiente de
inspección`. La ejecución posterior amplió la suite a **50/50** pruebas
aprobadas. El detalle, las limitaciones de verificación visual y las rutas de
los entregables v2 están en `reports/auditoria_intervenciones_v2.md`.
