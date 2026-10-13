# Fase 1 — Validación del entorno geoespacial

> Actualización final: la autenticación interactiva y las consultas de solo lectura
> ya se completaron en PostgreSQL 18.6 / PostGIS 3.6.2. Se verificaron ambas tablas.
> La malla RAW tiene etiqueta EPSG:9377 incoherente con sus coordenadas geográficas;
> el inventario original describía el CRS declarado, no su validez numérica.
> Consultar la [validación final](geospatial/validacion_final.md), que sustituye
> los estados pendientes y precisa esta discrepancia. Se conserva abajo el registro inicial.

Validación ejecutada con Python 3.14.3 del entorno del proyecto. GeoPandas 1.1.4,
Shapely 2.1.2, Pandas 3.0.6, PyProj 3.8.0, Pyogrio 0.13.0, SQLAlchemy 2.1.4 y
Psycopg 3.3.6 importados correctamente. Los dos conectores PostgreSQL no figuraban
en el requirements original; el módulo tendrá su archivo de dependencias adicional.
Las pruebas usarán unittest, incluido en Python; pytest no está instalado.

QGIS 3.44.15 está instalado en Windows. PyQGIS no pertenece al entorno virtual;
debe ejecutarse mediante el Python distribuido con QGIS. Su ejecución y la
validación del proyecto se realizan en la fase 5.

## Fuentes inspeccionadas

| Fuente | Registros | CRS |
|---|---:|---|
| Siniestros Medellín RAW | 235820 | atributos latitud/longitud; validación en fase 3 |
| Siniestros Comuna 3, original y limpio | 8332 cada uno | atributos latitud/longitud |
| Carrera 45 definitiva | 26 | EPSG:9377 |
| Carrera 45 preliminar | 27 | EPSG:9377 |
| Comunas | 23 | EPSG:9377 |
| Malla vial | 42792 | EPSG:9377 |
| Corredor previo | 1 | EPSG:9377 |
| Siniestros del corredor previo | 604 | atributos latitud/longitud |
| Documents/carrera45_revision.gpkg, carrera45_segmentos | 26 | EPSG:9377 |

El eje, el corredor, las comunas y el GeoPackage no tienen geometrías nulas,
vacías ni inválidas. La malla vial contiene una geometría nula; el primer
inventario cuenta también ese nulo como no válido. No se aplica reparación.
Los CSV no presentan filas completamente duplicadas. El RAW abarca 2019–2025.
El detalle de columnas, versiones, cantidades y hashes SHA-256 se encuentra en
[environment.json](geospatial/environment.json).

## PostgreSQL: verificación pendiente por autenticación

El servicio postgresql-x64-18 está en ejecución. Se intentó conectar a
localhost:5432, base movimanrique45, usuario postgres, con tiempo máximo de
conexión de 5 segundos, transacciones de solo lectura y consultas de hasta
15 segundos. El servidor solicitó contraseña (`no password supplied`).
No se verificaron todavía versiones SQL, tablas, columnas, conteos ni SRID de
la base. No se ejecutó ninguna escritura SQL. No se solicitaron secretos por chat.

El script [probe.py](../src/geospatial/probe.py) permite repetir la inspección
usando PGHOST, PGPORT, PGDATABASE, PGUSER y autenticación local de libpq (pgpass).
No almacena ni imprime contraseñas. Las fases locales pueden continuar; la
equivalencia con las tablas y consultas SQL anteriores queda pendiente.

## Resultados previos y conservación

El reporte anterior distingue 644 puntos a <=50 m y 604 dentro del buffer
recortado a Manrique. Estas cifras se recalcularán; no se usarán como resultados
fijos del módulo. No hay consultas SQL anteriores guardadas en la carpeta sql.
Se registraron hashes de todas las fuentes locales y del GeoPackage de revisión.
No se ejecutaron scripts antiguos que sobrescriben productos existentes.

Estado: validación local satisfactoria; componente PostgreSQL parcialmente bloqueado.
