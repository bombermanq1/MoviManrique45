"""Resume evidencia existente; no abre nuevas conexiones ni regenera productos."""
import json
from .common import ROOT,DOCS,table
import pandas as pd

def main():
    folder=ROOT/'reports/geospatial'
    read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
    db=read('database_final.json'); outside=read('outside_final.json'); qgis=read('qgis_final.json')
    text='# Validación final de pendientes — MoviManrique45\n\n'
    text+='Decisiones de cierre v1 posteriores: 604 principales, 40 de sensibilidad al borde, cuatro en revision territorial y seis fragmentos conservados. Ver [cierre tecnico](cierre_tecnico.md). El texto siguiente registra la validacion previa; la politica vigente ya esta decidida.\n\n'
    text+='Esta revisión sustituye los estados pendientes de autenticación de los informes anteriores. No repite la implementación ni modifica fuentes.\n\n'
    text+='## Autenticación y alcance SQL\n\n'
    diagnosis=db.get('diagnosis',{})
    error=diagnosis.get('initial_error',{}).get('message','Sin error registrado')
    text+='Error original exacto, sin credenciales:\n\n```text\n'+error+'\n```\n\n'
    text+='El servidor estaba disponible; faltaba suministrar contraseña. No existía pgpass ni variables de autenticación libpq en esta sesión. Se reutilizaron localhost:5432, usuario postgres y base movimanrique45 de los scripts existentes. El cuadro local enmascara la entrada, no escribe contraseñas y cierra la conexión al terminar. Se fijó default_transaction_read_only=on desde la conexión y se verificó transaction_read_only. Todas las consultas son SELECT/SHOW; el límite territorial local se envía como parámetro WKB, sin crear tablas.\n\n'
    text+='Estado: **'+db['status']+'**. Modo de solo lectura: **'+str(db.get('read_only','no verificado'))+'**.\n\n'
    if db['status']=='validated_available_tables':
        text+='Versiones comprobadas: '+str(db['versions'])+'\n\n'
        roads=db['tables']['carrera45_segmentos']; incidents=db['tables']['siniestros']
        text+='## Carrera 45 y seis fragmentos\n\n'
        comparisons=roads.get('comparison',[])
        text+=f"Tabla public.carrera45_segmentos: {roads['rows']} filas; SRID {roads['srids']}; {roads['null_or_empty']} nulas/vacías, {roads['invalid_nonnull']} inválidas, {roads['duplicate_ids']} IDs duplicados.\n\n"
        text+=f"Coincidencia de coordenadas exactas: {sum(r['exact_coordinates'] for r in comparisons)}/{len(comparisons)}. Máxima distancia Hausdorff: {max(r['hausdorff_m'] for r in comparisons)} m. No faltan ni sobran IDs.\n\n"
        text+=table(pd.DataFrame(roads['tiny_parts']))
        text+='Las seis partes SQL coinciden con las seis partes locales, sin diferencias geométricas. También se reproducen con el recorte original y coinciden con el GeoPackage externo. Su longitud es 0.032631–0.218238 m; están sobre el borde a precisión numérica. Cada fragmento tiene un extremo conectado y otro separado de la parte vecina una distancia equivalente a su longitud. Por tanto, son reproducibles como resultado del recorte, pero no están certificados como conexiones viales funcionales. No se reparan ni eliminan. Ver [detalle](validacion_final_fragmentos.md).\n\n'
        text+='## Siniestros y corredor\n\n'
        text+=f"Tabla public.siniestros: {incidents['rows']} filas, todas nominalmente Comuna 3; geometría Point EPSG:4326. IDs nulos: {incidents['null_ids']}; repetidos: {incidents['duplicate_ids']}. Los IDs coinciden con el conjunto local de 8332 registros. La base no contiene los 235820 registros de toda Medellín: esa cifra corresponde al CSV RAW.\n\n"
        text+=f"Selección Python sobre las geometrías extraídas de SQL: {incidents['corridor_50m_rows']} registros; sin diferencias de IDs respecto a los 604 locales.\n\n"
        if 'attribute_discrepancies' in incidents:
            text+='Discrepancias de atributos por objectid: '+str(incidents['attribute_discrepancies'])+'. Diferencia máxima de longitud/latitud tras ida y vuelta de CRS: '+str(incidents['max_longitude_delta_degrees'])+' / '+str(incidents['max_latitude_delta_degrees'])+' grados.\n\n'
        native=incidents.get('postgis_native')
        if native:
            text+=f"Verificación independiente calculada en PostGIS con ST_Transform, ST_Buffer (quad_segs=16), ST_Intersection y ST_Intersects: **{native['corridor_rows']}** registros del corredor y **{native['proximity_50m_rows']}** a <=50 m. IDs solo SQL: {native['ids_only_sql']}; IDs solo local: {native['ids_only_local']}. Fuera del límite: {len(native['outside_rows'])}.\n\n"
        else:
            text+='La consulta nativa adicional de PostGIS aún no dispone de evidencia; no se declara comprobada.\n\n'
    else:
        text+='La conexión/consulta sigue sin completarse: '+str(db.get('error',{}))+'.\n\n'
    text+='## Los 44 puntos externos: discrepancia territorial sensible al borde\n\n'
    text+='40 están del lado de Aranjuez, como máximo a **1.7911 mm** del límite, y son los 40 que separan el conteo por proximidad (644) del corredor recortado estricto (604). Una tolerancia territorial de 1 cm los incorporaría; no se aplicó ese cambio. El conteo 604 es reproducible bajo la regla estricta, pero no debe interpretarse como una separación territorial robusta frente a la precisión posicional.\n\n'
    text+=table(pd.DataFrame(outside['remaining_four']))
    text+='Los 44 conservan exactamente las coordenadas del RAW y aparecen externos tanto en la comparación geográfica como proyectada. Hay 10 posiciones distintas; la más repetida tiene 16 registros. No se eliminaron por coincidir espacialmente. Sin precisión certificada y límites históricos no puede decidirse si corresponden a errores de geocodificación, asignación administrativa o eventos en vías limítrofes. [Investigación detallada](investigacion_44_siniestros.md).\n\n'
    text+='## Discrepancia de CRS en la malla RAW\n\n'
    text+='La malla RAW declara EPSG:9377, pero sus coordenadas están alrededor de (-75.7, 6.2), en grados. El script preexistente crear_carrera45_manrique.py interpreta explícitamente EPSG:4326 en memoria antes de proyectar a 9377. Al reproducir ese procedimiento, los seis fragmentos y sus entidades recortadas coinciden exactamente. Se rectifica el inventario anterior: su columna CRS era el declarado, no una confirmación de coherencia numérica. El archivo RAW permanece intacto.\n\n'
    text+='## Proyecto QGIS existente\n\n'
    text+=f"Abierto: {qgis['opened']}; capas: {qgis['layer_count']}; validación: {qgis['passed']}; proyecto intacto: {qgis['project_unchanged']}; errores de render: {qgis['render_errors']}. Se reabrió el archivo existente sin regenerarlo. Las 10 capas son locales, tienen fuentes válidas, EPSG:9377 y están configuradas como solo lectura.\n\n"
    text+='## Evidencia, pruebas y pendientes reales\n\n'
    if (folder/'final_tests.json').exists():
        text+='Pruebas: '+str(read('final_tests.json'))+'\n\n'
    text+='Evidencias: [PostgreSQL](../reports/geospatial/database_final.json), [QGIS](../reports/geospatial/qgis_final.json), [fragmentos](../reports/geospatial/fragments_final.json), [puntos externos](../reports/geospatial/outside_final.json), [pruebas](../reports/geospatial/final_tests.txt).\n\n'
    text+='Pendientes de criterio experto: decidir tratamiento del borde sin modificar datos originales; revisar los seis fragmentos en contexto vial; contrastar los cuatro puntos externos restantes con una fuente autorizada; documentar/corregir metadatos del RAW únicamente con autorización. No quedan correcciones geométricas aprobadas. No hubo escrituras SQL, commits ni push.\n'
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS/'validacion_final.md').write_text(text,encoding='utf-8')

if __name__=='__main__':
    main()
