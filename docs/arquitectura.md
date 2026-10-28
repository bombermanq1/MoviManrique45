# Arquitectura y mantenimiento

El proyecto prepara datos con Python y los publica como archivos de consulta.
La web estática lee esos archivos en el navegador. Streamlit es una segunda
interfaz y se inicia por separado.

El [README principal](../README.md) está en la raíz. Las guías y los reportes
Markdown están en `docs/`. De `reports/` se versionan diez evidencias de
`geospatial/` utilizadas por pruebas y scripts. Los demás reportes,
registros de ejecución y capturas permanecen locales y están excluidos de Git.

## Del dato a la interfaz

`src/ingestion/` consulta las fuentes ArcGIS y guarda las copias originales en
`data/raw/`. Los módulos de `src/etl/` y `src/geospatial/` preparan y
validan los productos derivados.

`src/dashboard/datos.py` reúne los insumos del dashboard y comprueba el cierre.
`src/dashboard/intervenciones.py` construye las fichas. El exportador
`src/dashboard/exportar_web.py` escribe los dos JSON de `web/data/`.
El iniciador `scripts/iniciar_demo.ps1` valida, exporta y sirve la aplicación.

Un clon puede mostrar una exportación existente si incluye los dos JSON. Para
volver a generarlos necesita los insumos locales de
[manifest_demo_v1.json](../data/manifest_demo_v1.json).

## Frontend

```text
web/
├── index.html
├── assets/
│   └── manrique-constelaciones-2023.jpg
├── css/
│   └── styles.css
├── js/
│   ├── app.js
│   ├── datos.js
│   ├── mapa.js
│   └── intervenciones.js
└── data/
    ├── dashboard.json
    └── intervenciones.json
```

`index.html` contiene la estructura, los controles y el contenido de contexto.
Carga una hoja de estilos y `app.js` como módulo. No hay estilos ni
JavaScript incrustados en el documento.

| Archivo | Responsabilidad |
|---|---|
| `css/styles.css` | Colores, componentes y reglas de escritorio, tablet y móvil. |
| `js/app.js` | Arranque, navegación, filtros, indicadores, gráficos y coordinación de la zona seleccionada. |
| `js/datos.js` | Lectura de los dos JSON, validación de contratos y funciones compartidas de formato. |
| `js/mapa.js` | Representación SVG, capas, zoom, arrastre, teclado y encuadre. |
| `js/intervenciones.js` | Selector, fichas, catálogo y tabla comparativa de zonas. |

El estado de la selección vive en `app.js`. Un cambio de filtro actualiza las
tarjetas, gráficos y puntos. Un cambio de zona sincroniza mapa, selector y
ficha. Las fichas mantienen sus cifras históricas completas.

Los paneles de metodología y propuestas usan elementos HTML `details`.
La navegación abre el panel al que apunta un enlace, incluso si estaba
cerrado. La fotografía se sirve desde `assets/`; la portada no necesita
consultar un proveedor de imágenes para cargar.

Los cálculos del mapa convierten coordenadas geográficas a posiciones en la
pantalla. No vuelven a calcular el corredor ni la pertenencia de los siniestros.
Por ejemplo, **Acercar al eje** solo cambia el encuadre: no cambia registros,
distancias ni geometrías.

Al cambiar el diseño, conserva los IDs de controles o actualiza sus lectores y
pruebas. Los valores usados en anchuras de barras son estilos dinámicos de
presentación; las reglas visuales compartidas están en el CSS. El texto
procedente de los JSON se escapa antes de incluirse en HTML.

### Fotografía de la portada

La imagen [Constelaciones en Manrique](https://commons.wikimedia.org/wiki/File:Constelaciones_en_Manrique.jpg)
es de la Agencia para la Gestión del Paisaje, el Patrimonio y las Alianzas
Público Privadas, tomada el 5 de mayo de 2023. Se utiliza una miniatura de
960 × 720 px de Wikimedia Commons bajo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
El archivo [local](../web/assets/manrique-constelaciones-2023.jpg) se conserva
sin retoque; CSS adapta su encuadre. La atribución y la licencia están visibles
en la portada y ampliadas en metodología. Si se redistribuye o modifica la
foto, deben conservarse sus créditos y las condiciones de esa licencia.

La imagen aporta contexto de Manrique. No representa una inspección ni se
presenta como una fotografía del corredor de Carrera 45.

## Validar un cambio

Para una modificación de interfaz, comprueba la carga de recursos, una selección
vacía, filtros combinados, las capas del mapa y las 12 fichas. La prueba de
navegador también sirve la web bajo `/movimanrique45/` para detectar referencias
que solo funcionarían en la raíz. Los comandos están en
[instalación y pruebas](instalacion.md).

Las pruebas de Python protegen la partición de eventos y los IDs de los
conjuntos 604/40/4. Las evidencias de `reports/geospatial/` registran
ejecuciones anteriores: una validación SQL guardada no acredita el estado
actual de PostgreSQL.

## Regenerar productos

El pipeline `src.geospatial.pipeline` vuelve a escribir productos derivados,
incluidos GeoPackage, CSV, capas web y reportes. No es un comando de consulta.
Una ejecución incompleta puede dejar productos de distintas ejecuciones;
comprueba todo el resultado antes de exportarlo a los consumidores.

No ejecutes las ingestas para probar un cambio de CSS o JavaScript. Sus salidas
pueden sobrescribir las copias locales. Para revisar la web utiliza los JSON
existentes y un servidor HTTP, como se explica en la guía de instalación.

## Otras herramientas

[app.py](../app.py) conserva la interfaz Streamlit. Sus dependencias adicionales
están en `requirements_mvp.txt`. No utiliza los módulos de `web/js/`.

El proyecto [QGIS](../qgis/MoviManrique45_Analisis.qgz) usa rutas relativas a los
GeoPackage, capas en EPSG:9377 y configuración de solo lectura. Cierra QGIS
antes de regenerar archivos que tenga abiertos.

Los recursos de Power BI se describen en [su guía](powerbi.md). Son consultas
y medidas preparadas para importar; no constituyen un PBIX/PBIP validado.
