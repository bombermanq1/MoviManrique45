# Diseño propuesto: cuatro páginas

Propuesta para implementar posteriormente en Power BI Desktop; no es una captura
de un reporte construido. Valores de referencia: versión cierre_v1, 2019–2025.

## Sistema visual

Lienzo 1440×900, fondo #F5F7FA; tarjetas blancas; texto #172B4D; tipografía Segoe
UI, título 26–30 px, subtítulos 16–18 px, ejes/etiquetas 12–14 px. Márgenes 24 px,
separaciones 16 px, máximo seis visuales principales por página. Tabulación lógica,
texto alternativo en mapas y gráficos, contraste verificado antes de publicación.

| Significado estable | Color | Uso |
|---|---|---|
| Corredor principal | #007C83 | Tarjeta y serie destacada |
| Sensibilidad al borde | #B86E00 | Etiqueta ámbar, siempre con texto |
| Revisión territorial | #9C3D58 | Casos por revisar, no riesgo |
| Resto de Manrique | #66758C | Contexto |
| Prioridad exploratoria | #6D4C91 | Contorno de zonas, no semáforo de peligrosidad |

No reutilizar colores de categoría para implicar niveles de gravedad. Gravedad
y tipo se muestran en barras horizontales con etiquetas y colores neutros. Sin
gráficos 3D, velocímetros ni mapas de calor presentados como riesgo.

Cabecera común: MoviManrique45, título de página, período seleccionado y botón
Restablecer. Navegación inferior con cuatro pestañas. Año y barrio nominal
sincronizados en páginas 1–3; filtros de territorio geométrico y zona locales a
página 3. Página 4 muestra calidad del cierre completo por defecto, con su propio
filtro temporal para eventos; los seis fragmentos no cambian con el año.

## Página 1 — Resumen general

Pregunta: ¿cómo se distribuyen los registros disponibles de Comuna 3?

| Región del lienzo | Visual / campos / comportamiento |
|---|---|
| Cabecera, y=24–90 | Título, versión, período; botones de navegación |
| Filtros, y=100–155 | Año (multiselección), barrio nominal; sin filtro automático por corredor |
| Tarjetas, y=175–280 | Total 8332; principal 604; participación 7.25%; período 2019–2025 (valores sin filtros) |
| Centro izquierdo, x=24–900, y=310–560 | Línea/columnas: DimFecha[Año] y [Registros], orden ascendente |
| Centro derecho, x=920–1416 | Barras gravedad: 6781 HERIDOS / 1551 DAÑOS; etiqueta «registros», no personas |
| Inferior izquierdo, y=590–820 | Barras tipo: CHOQUE 3711, OTRO 2046, ATROPELLO 1513, CAIDA OCUPANTE 536, VOLCAMIENTO 526 |
| Inferior derecho | Matriz compacta año × categoría, total conciliable a 8332 |

Seleccionar una barra filtra los demás gráficos y tarjetas; el porcentaje global
de corredor ignora el barrio por definición y muestra esa condición en tooltip.
Alternativa si se prefiere coherencia local: ocultar esa tarjeta bajo filtro de
barrio y mostrarla solo en página 2 con su denominador explicado. No permitir que
una etiqueta «total Comuna 3» se mantenga sin avisar después de filtrar un barrio:
usar «Registros en selección» y título dinámico del contexto.

## Página 2 — Carrera 45

Pregunta: ¿qué se observa en el corredor estricto y cómo se compara descriptivamente?

| Región | Visual y regla |
|---|---|
| Filtros | Año, barrio nominal; los visuales principales usan [Registros corredor], no un filtro de página sobre el flag |
| Tarjetas | Principal 604; participación corredor/Comuna 3 7.25%; mediana de distancia de los registros del corredor (calcular, no fijar un valor inventado) |
| Centro ancho | Dos paneles alineados por año: conteo Comuna 3 y conteo corredor, con escalas explícitas; sin doble eje engañoso |
| Lateral | Gravedad del corredor: 534 HERIDOS / 70 DAÑOS |
| Inferior | Tipo del corredor: 288 CHOQUE, 172 ATROPELLO, 93 OTRO, 30 CAIDA OCUPANTE, 21 VOLCAMIENTO |
| Nota visible | «40 casos sensibles al borde fuera del indicador principal. Proximidad no implica atribución a la vía.» |

El corredor anual esperado sin filtros adicionales es 86,45,36,115,111,95,116
para 2019–2025. Comparar conteos/cambios porcentuales, nunca tasas de riesgo.
El porcentaje compara la misma ventana temporal y selección de gravedad/tipo;
su denominador es Comuna 3 nominal completa, ignorando filtros espaciales.

## Página 3 — Análisis geográfico

Pregunta: ¿dónde están los registros y las zonas exploratorias del cierre?

Composición: filtros arriba; mapa 65% del ancho; tabla de zonas/revisión 35%;
leyenda y nota metodológica al pie. Usar dos vistas mediante marcadores de
presentación (sin capturar filtros de datos):

1. **Eventos y eje:** puntos con latitud/longitud de la unión auxiliar; color por
   categoria_analisis, tooltip con ID técnico, año, gravedad, tipo y distancia.
   Eje como referencia GeoJSON local; no geocodificar por nombre de barrio.
2. **Zonas exploratorias:** referencia vinculada por zona_id de las 12 prioridades;
   color/intensidad por [Registros] de la selección, contorno por prioridad fija.
   Tabla con zona_id y conteo filtrado. No recalcular el percentil por interacción.

Azure Maps admite referencias GeoJSON y vinculación por propiedades comunes;
validar correspondencia y filtros en Desktop antes de prometer interacción.
[Referencia oficial](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-add-reference-layer).

Los GeoJSON existentes son EPSG:4326: carrera45 (26), prioridades (12), fragmentos
(6) y concentraciones (342). El archivo de 342 celdas suprime conteos <5, por lo
que no representa las 439 celdas analíticas completas. Para una futura vista de
las 439 celdas se necesitaría una nueva exportación autorizada del GPKG; no se
genera en esta fase. La vista de 12 prioridades ya dispone de todas sus geometrías.

No se garantiza una única superposición simultánea de todas las capas: se probará
el visual y su versión. Las dos vistas propuestas evitan esa dependencia. Si
Azure Maps no está habilitado por la organización, se conservará tabla geográfica
y referencia QGIS; no se afirmará que hay un mapa interactivo operativo.

Filtros: barrio nominal, territorio geométrico, categoría, zona y prioridad.
Mostrar SIN_ZONA en la tabla para no esconder los 44 externos. La tabla de
revisión puede filtrar los puntos por ID. Polígonos estáticos no deben aparentar
filtrar eventos si el enlace de referencia no se ha verificado.

Las coordenadas individuales son para uso analítico controlado; cualquier futura
publicación debe decidir expresamente el nivel de detalle. No se publican ahora.

## Página 4 — Calidad y trazabilidad

| Región | Contenido |
|---|---|
| Tarjetas | 40 sensibilidad al borde; cuatro revisión territorial; seis fragmentos conservados; integridad de IDs 604/604 |
| Centro izquierdo | Tabla de cuatro casos externos: ID, territorio nominal/geométrico, distancia al límite y estado; no direcciones/radicados |
| Centro derecho | Tabla de seis partes: parte_id, objectid, longitud, origen_documentado, decision_version |
| Inferior | Fuentes/versión, fechas, control CRS y limitaciones con texto legible |

Calidad de coordenadas: 8332 pasan el rango validado; eso no prueba exactitud
posicional. 40 están a máximo 1.79 mm del límite, cuatro a 3.73–26.68 m. La malla
RAW declara 9377 con coordenadas geográficas: advertencia conocida, no indicador
verde de «CRS correcto». Fragmentos preservados y reproducibles por recorte.

Las tarjetas de fragmentos/versión no responden al año de los siniestros. Los
conteos de casos sí pueden responder a un filtro local de año, rotulados «en
selección»; incluir al lado los totales fijos 40/4 del cierre para trazabilidad.
No sincronizar el filtro de corredor de otra página: ocultaría precisamente los
problemas que esta página debe mostrar.

## Validación del diseño antes de publicar

Sin filtros: 8332/604/40/4/7684, 12 prioridades, seis fragmentos. Filtrar 2025:
1145 totales y 116 principales. Seleccionar sensibilidad: 40 filas y ninguna
incorporada al principal; no utilizar esa categoría para inflar el denominador.
Revisar tooltips, navegación por teclado, contraste, exportación de tablas y
persistencia de filtros. Ninguna de estas interacciones está ejecutada todavía.
