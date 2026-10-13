# Módulo geoespacial MoviManrique45

## Versión de cierre v1

Se adoptan las decisiones del [cierre técnico](../../reports/geospatial/cierre_tecnico.md):
604 principales, 40 de sensibilidad al borde, cuatro en revisión territorial y
seis fragmentos conservados. El proceso verifica las listas de IDs aprobadas y
la incoherencia conocida entre el CRS declarado de la malla RAW y sus coordenadas.
No modifica originales ni amplía el indicador por tolerancia territorial.

Para comprobar el cierre: ejecutar pipeline dos veces y luego run_tests --final.
La reproducibilidad compara fuentes, configuración y código, hashes lógicos de
capas y hashes binarios de CSV/GeoJSON. Los metadatos internos de GPKG no se usan
para exigir igualdad binaria. Las pruebas de SQL utilizan la evidencia final
guardada; este cierre no solicita de nuevo credenciales ni escribe en la base.

La [validación final](../../reports/geospatial/validacion_final.md) incluye el
contraste PostgreSQL/PostGIS y la investigación de los 44 puntos externos.
Para repetir exclusivamente los pendientes, sin regenerar productos:

```powershell
.\.venv\Scripts\python.exe -m src.geospatial.validate_database --interactive
.\.venv\Scripts\python.exe -m src.geospatial.validate_outside
.\.venv\Scripts\python.exe -m src.geospatial.validate_fragments
& 'C:\Program Files\QGIS 3.44.15\bin\python-qgis-ltr.bat' src/geospatial/validate_qgis.py
.\.venv\Scripts\python.exe -m src.geospatial.run_tests --final
.\.venv\Scripts\python.exe -m src.geospatial.final_report
```

La opción interactive abre un cuadro local con entrada enmascarada únicamente
si falla la autenticación existente. No persiste la contraseña. Las pruebas
finales contrastan las evidencias JSON guardadas; para una nueva comprobación
del estado de la base debe ejecutarse primero el validador interactivo.

Analiza las fuentes locales existentes sin descargarlas de nuevo ni alterar RAW,
GeoJSON anteriores, GeoPackage de revisión o tablas PostgreSQL. Las mediciones
usan EPSG:9377; la exportación web usa EPSG:4326. No atribuye causalidad ni riesgo.

## Ejecución desde la raíz del proyecto

```powershell
# Inspección de fuentes y conexión PostgreSQL de solo lectura.
.\.venv\Scripts\python.exe -m src.geospatial.probe

# Auditoría, análisis, Power BI y GeoJSON. Repetir para verificar reproducibilidad.
.\.venv\Scripts\python.exe -m src.geospatial.pipeline
.\.venv\Scripts\python.exe -m src.geospatial.pipeline

# Pruebas y evidencia persistente.
.\.venv\Scripts\python.exe -m src.geospatial.run_tests

# Proyecto QGIS, relectura y render sin abrir una ventana.
& 'C:\Program Files\QGIS 3.44.15\bin\python-qgis-ltr.bat' src/geospatial/build_qgis.py
```

Dependencias adicionales en [requirements.txt](requirements.txt), que incluye las
dependencias base. No fue necesario instalar paquetes en esta ejecución.
PyQGIS usa su propio Python 3.12; no se instala dentro del entorno Python 3.14.
Para otro equipo, adaptar la ruta de QGIS y crear un entorno compatible antes de
instalar los requisitos. La conexión SQL es opcional para el procesamiento local.

El script de inspección admite PGHOST, PGPORT, PGDATABASE y PGUSER; los valores
por defecto son localhost, 5432, movimanrique45 y postgres. Usar autenticación
local libpq mediante pgpass (Windows: `%APPDATA%\postgresql\pgpass.conf`) o el
mecanismo seguro ya utilizado en el equipo. No guardar contraseñas en el código.
Todas las conexiones que crea el módulo fijan default_transaction_read_only=on.
No se ejecutan los scripts antiguos de carga a PostGIS.

## Entradas, configuración y ejecución repetida

- Siniestros: [RAW](../../data/raw/siniestros_medellin.csv), filtrado por `num_comuna=Comuna 3`.
- Eje: [26 entidades definitivas](../../data/processed/carrera45_manrique.geojson).
- Límite: [comunas oficiales](../../data/raw/comunas_medellin.geojson), código 03.
- Comparación: CSV de Comuna 3 y CSV previo del corredor de 50 m.
- Revisión opcional: `Documents/carrera45_revision.gpkg` del usuario del equipo.
- [config.json](config.json): tolerancias de extremos, longitud diminuta, distancias,
  cuadrícula, percentil y mínimo de registros por celda web.

Las distancias del corredor principal (50 m), entorno prioritario (100 m), margen
de control local (0.1 grados) y CRS de entrada de coordenadas (4326) son parte de la
metodología fija de esta versión. El parámetro de distancias configura la tabla
de sensibilidad, no redefine el corredor principal.

Validaciones de esquema e IDs fallan explícitamente si las fuentes cambian de
forma incompatible. No se inventan CRS ni se reparan geometrías. Fechas y
coordenadas no válidas se señalan; filas no georreferenciables permanecen en la
tabla de hechos con atributos espaciales nulos. El módulo no deduplica por
coincidencias de fecha, lugar o radicado.

El proceso reemplaza únicamente sus productos en carpetas dedicadas; no agrega
filas en cada ejecución. Los GeoPackage se escriben primero en archivos staging
y se releen antes del reemplazo. Si queda un `.tmp.gpkg` de una ejecución fallida,
el proceso se detiene para revisión. Cerrar QGIS antes de regenerar capas en Windows.
Una ejecución fallida puede dejar productos de fases anteriores actualizados;
consumirlos solo tras revisar el éxito del proceso y las pruebas. No hay transacción
única que abarque todos los archivos.

El manifiesto [run.json](../../reports/geospatial/run.json) registra parámetros,
hashes SHA-256 de fuentes y hashes lógicos de capas/tablas. Compara ejecuciones
con las mismas entradas y configuración. No se exige igualdad binaria de GPKG
ni QGZ: pueden contener metadatos temporales. Las fuentes se verifican antes y
después de procesar y nuevamente en las pruebas. El registro de errores se guarda
en `reports/geospatial/pipeline.log` (ignorado por Git).

## Productos y método

- [Auditoría](../../reports/auditoria_geometrica_carrera45.md): entidades y partes,
  longitudes, extremos, vecinos, intersecciones y candidatos de discontinuidad.
- [Análisis de siniestros](../../reports/analisis_espacial_siniestros.md): calidad,
  temporalidad, comparación de distancias y concentración en celdas de 100 m.
- [Proyecto QGIS](../../qgis/MoviManrique45_Analisis.qgz) y [guía](../../qgis/README.md).
- [Power BI](../../powerbi/geospatial/README.md): hechos, dimensiones y resúmenes.
- [Diccionario](../../reports/geospatial/diccionario_datos.md).
- [Integración web](../../reports/geospatial/integracion_web.md).
- [Resumen de fases y limitaciones](../../reports/geospatial/resumen_implementacion.md).

Los GeoPackage y GeoJSON están dentro de `data/processed/geospatial/`, que ya
está excluida por el .gitignore del proyecto. Distribuir esas capas junto al QGZ
cuando se traslade el proyecto; el QGZ por sí solo no incluye los datos.

La prioridad es exploratoria por frecuencia observada; sin aforos, exposición y
evaluación de cobertura no equivale a peligro, tasa de riesgo ni efecto de una vía.
Las capas web contienen agregados y geometría vial; no contienen eventos individuales.
