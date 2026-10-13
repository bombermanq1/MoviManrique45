# Power BI — auditoría y propuesta de diseño

Estado: **documentación y propuesta; no hay PBIX/PBIP construido ni medidas ejecutadas en Power BI**.
Se conservaron los datasets y los resultados geoespaciales. No se abrió PostgreSQL.

## Entregables

1. [Inventario y auditoría detallada](auditoria.md): los 12 CSV, sus columnas,
   tipos inferidos, nulos, cardinalidades, claves y controles.
2. [Modelo y relaciones](modelo.md): estrella recomendada, claves y filtros.
3. [Diseño de cuatro páginas](dashboard.md): composición, visuales e interacciones.
4. [Medidas DAX propuestas](medidas_dax.md): definiciones y comportamiento de filtros.
5. [Power Query e implementación futura](preparacion_desktop.md): transformaciones
   propuestas, secuencia de construcción y viabilidad PBIP.

## Resultado de la auditoría

| Control | Resultado comprobado |
|---|---:|
| Hechos / IDs únicos | 8332 / 8332 |
| Principal estricto 50 m | 604 |
| Sensibilidad al borde | 40 |
| Revisión territorial | 4 |
| Resto de Manrique | 7684 |
| Zonas analíticas / prioritarias | 439 / 12 |
| Segmentos / fragmentos conservados | 26 / 6 |
| Territorios nominales (comuna, barrio) | 18 |
| Territorios geométricos | 4 |
| Gravedades / tipos de siniestro | 2 / 5 |
| Meses observados | 84, de 2019 a 2025 |

Las tres listas 604/40/4 coinciden por ID con el cierre aprobado. Los conteos por
zona concuerdan con los hechos; los 44 eventos externos tienen zona_id nulo y no
son errores de integridad. La dimensión de clasificación incluye una quinta
categoría de reserva, sin_posicion_validada, sin registros actuales.

La tabla de hechos no contiene fecha diaria ni latitud/longitud. Para construir
la dimensión de fechas y el mapa de eventos se propone una unión 1:1, dentro de
Power Query, con cuatro columnas del CSV procesado existente. Se verificaron
8332 correspondencias, fechas válidas y concordancia año/mes. No se creó ese
dataset enriquecido ni se modificaron los archivos actuales.

La gravedad observada contiene HERIDOS (6781) y DAÑOS (1551). No presentar la
ausencia de una categoría MUERTOS como evidencia de cero fallecimientos reales.
El campo `muertos` en zonas es un conteo de registros según categoría, no personas.

## Alcance y pendientes

Se detectó Power BI Desktop Microsoft Store **2.158.1304.0**. PBIP es una opción
viable para una fase posterior, pero aún no se ha probado abrir, refrescar,
guardar ni renderizar un proyecto en esta instalación. La propuesta DAX/M
requiere pruebas en el motor de Power BI antes de declarar un dashboard funcional.

El mensaje recibido termina en «3. Relaciones entre». El alcance anterior
permite entregar la auditoría y el diseño; no se asumieron instrucciones
adicionales después de ese fragmento.

[auditoria.json](auditoria.json) conserva evidencia estructurada y hashes de las
fuentes inspeccionadas. El script de auditoría escribe solo en esta carpeta.
No se ejecutó el pipeline geoespacial, ningún commit/push ni trabajo de frontend/backend.
