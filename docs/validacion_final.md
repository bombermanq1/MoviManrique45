# Validación final de pendientes — MoviManrique45

> Evidencia de una ejecución anterior del cierre geoespacial. Se conservan
> sus resultados y tablas; no equivale a una nueva comprobación de PostgreSQL
> ni a las pruebas del frontend. Para el funcionamiento actual, consulta la
> [arquitectura](arquitectura.md).


> Decisiones posteriores para la versión actual: 604 IDs estrictos como indicador
> principal; 40 en sensibilidad al borde sin incorporarlos; cuatro en revisión
> territorial; seis fragmentos conservados. El tratamiento de esta versión ya
> está decidido; la revisión humana no habilita cambios automáticos. Ver
> [cierre técnico](cierre_tecnico.md). Se conserva abajo la evidencia de validación previa.

Esta revisión sustituye los estados pendientes de autenticación de los informes anteriores. No repite la implementación ni modifica fuentes.

## Autenticación y alcance SQL

Error original exacto, sin credenciales:

```text
connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
```

El servidor estaba disponible; faltaba suministrar contraseña. No existía pgpass ni variables de autenticación libpq en esta sesión. Se reutilizaron localhost:5432, usuario postgres y base movimanrique45 de los scripts existentes. El cuadro local enmascara la entrada, no escribe contraseñas y cierra la conexión al terminar. Se fijó default_transaction_read_only=on desde la conexión y se verificó transaction_read_only. Todas las consultas son SELECT/SHOW; el límite territorial local se envía como parámetro WKB, sin crear tablas.

Estado: **validated_available_tables**. Modo de solo lectura: **on**.

Versiones comprobadas: ['movimanrique45', 'PostgreSQL 18.6 on x86_64-windows, compiled by msvc-19.44.35229, 64-bit', 'POSTGIS="3.6.2 3.6.2" [EXTENSION] PGSQL="180" GEOS="3.14.1dev-CAPI-1.20.4" PROJ="8.2.1 NETWORK_ENABLED=OFF URL_ENDPOINT= USER_WRITABLE_DIRECTORY=C:\\WINDOWS\\ServiceProfiles\\NetworkService\\AppData\\Local/proj" (compiled against PROJ 8.2.1) LIBXML="2.12.5" LIBJSON="0.12" LIBPROTOBUF="1.2.1" WAGYU="0.5.0 (Internal)"']

## Carrera 45 y seis fragmentos

Tabla public.carrera45_segmentos: 26 filas; SRID [9377]; 0 nulas/vacías, 0 inválidas, 0 IDs duplicados.

Coincidencia de coordenadas exactas: 26/26. Máxima distancia Hausdorff: 0.0 m. No faltan ni sobran IDs.

```text
 objectid path  length_m equal_local_parts
     7611   []  0.087723          [7611:1]
    20909  [1]  0.069021         [20909:1]
    20909  [2]  0.035759         [20909:2]
    24568  [1]  0.218238         [24568:1]
    28471  [1]  0.127048         [28471:1]
    28471  [2]  0.032631         [28471:2]
```
Las seis partes SQL coinciden con las seis partes locales, sin diferencias geométricas. También se reproducen con el recorte original y coinciden con el GeoPackage externo. Su longitud es 0.032631–0.218238 m; están sobre el borde a precisión numérica. Cada fragmento tiene un extremo conectado y otro separado de la parte vecina una distancia equivalente a su longitud. Por tanto, son reproducibles como resultado del recorte, pero no están certificados como conexiones viales funcionales. No se reparan ni eliminan. Ver [detalle](validacion_final_fragmentos.md).

## Siniestros y corredor

Tabla public.siniestros: 8332 filas, todas nominalmente Comuna 3; geometría Point EPSG:4326. IDs nulos: 0; repetidos: 0. Los IDs coinciden con el conjunto local de 8332 registros. La base no contiene los 235820 registros de toda Medellín: esa cifra corresponde al CSV RAW.

Selección Python sobre las geometrías extraídas de SQL: 604 registros; sin diferencias de IDs respecto a los 604 locales.

Discrepancias de atributos por objectid: {'fecha_siniestro': 0, 'gravedad_siniestro': 0, 'clase_siniestro': 0}. Diferencia máxima de longitud/latitud tras ida y vuelta de CRS: 1.4210854715202004e-14 / 5.329070518200751e-15 grados.

Verificación independiente calculada en PostGIS con ST_Transform, ST_Buffer (quad_segs=16), ST_Intersection y ST_Intersects: **604** registros del corredor y **644** a <=50 m. IDs solo SQL: []; IDs solo local: []. Fuera del límite: 44.

## Los 44 puntos externos: discrepancia territorial sensible al borde

40 están del lado de Aranjuez, como máximo a **1.7911 mm** del límite, y son los 40 que separan el conteo por proximidad (644) del corredor recortado estricto (604). Una tolerancia territorial de 1 cm los incorporaría; no se aplicó ese cambio. El conteo 604 es reproducible bajo la regla estricta, pero no debe interpretarse como una separación territorial robusta frente a la precisión posicional.

```text
 objectid           territorio_geometrico  distancia_limite_m  distancia_carrera45_m
   125795 90:Corregimiento de Santa Elena            3.730551            1849.898916
   140908 90:Corregimiento de Santa Elena           15.664917            1536.991509
   154532 90:Corregimiento de Santa Elena           15.664917            1536.991509
   192142                      01:Popular           26.684032             250.790112
```
Los 44 conservan exactamente las coordenadas del RAW y aparecen externos tanto en la comparación geográfica como proyectada. Hay 10 posiciones distintas; la más repetida tiene 16 registros. No se eliminaron por coincidir espacialmente. Sin precisión certificada y límites históricos no puede decidirse si corresponden a errores de geocodificación, asignación administrativa o eventos en vías limítrofes. [Investigación detallada](investigacion_44_siniestros.md).

## Discrepancia de CRS en la malla RAW

La malla RAW declara EPSG:9377, pero sus coordenadas están alrededor de (-75.7, 6.2), en grados. El script preexistente crear_carrera45_manrique.py interpreta explícitamente EPSG:4326 en memoria antes de proyectar a 9377. Al reproducir ese procedimiento, los seis fragmentos y sus entidades recortadas coinciden exactamente. Se rectifica el inventario anterior: su columna CRS era el declarado, no una confirmación de coherencia numérica. El archivo RAW permanece intacto.

## Proyecto QGIS existente

Abierto: True; capas: 10; validación: True; proyecto intacto: True; errores de render: []. Se reabrió el archivo existente sin regenerarlo. Las 10 capas son locales, tienen fuentes válidas, EPSG:9377 y están configuradas como solo lectura.

## Evidencia, pruebas y pendientes reales

Pruebas: {'tests': 22, 'failures': 0, 'errors': 0, 'successful': True}

Evidencias: [PostgreSQL](../reports/geospatial/database_final.json), [QGIS](../reports/geospatial/qgis_final.json), [fragmentos](../reports/geospatial/fragments_final.json), [puntos externos](../reports/geospatial/outside_final.json), [pruebas](../reports/geospatial/final_tests.txt).

Pendientes de criterio experto: decidir tratamiento del borde sin modificar datos originales; revisar los seis fragmentos en contexto vial; contrastar los cuatro puntos externos restantes con una fuente autorizada; documentar/corregir metadatos del RAW únicamente con autorización. No quedan correcciones geométricas aprobadas. No hubo escrituras SQL, commits ni push.
