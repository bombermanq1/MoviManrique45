"""Informe del cierre aprobado y listado comprobado de archivos afectados."""
import json
from pathlib import Path
import pandas as pd
from .common import ROOT,DOCS,table,json_write
from .probe import digest

def main():
    folder=ROOT/'reports/geospatial'
    manifest=json.loads((folder/'run.json').read_text(encoding='utf-8'))
    tests=json.loads((folder/'final_tests.json').read_text(encoding='utf-8'))
    qgis=json.loads((folder/'qgis_final.json').read_text(encoding='utf-8'))
    if not manifest['reproducible'] or not tests['successful'] or not qgis['passed']:
        raise RuntimeError('No cerrar sin reproducibilidad, pruebas y QGIS satisfactorios.')
    before=json.loads((folder/'cierre_archivos_antes.json').read_text(encoding='utf-8'))
    DOCS.mkdir(parents=True, exist_ok=True)
    report_path=DOCS/'cierre_tecnico.md'
    report_path.touch(exist_ok=True)
    inventory_path=folder/'cierre_archivos.json'
    if not inventory_path.exists():
        inventory_path.write_text('{}',encoding='utf-8')
    paths=[p for base in ['src/geospatial','tests','powerbi/geospatial','reports','docs','qgis','data/processed/geospatial']
        for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    changed=[]
    for path in sorted(paths):
        relative=path.relative_to(ROOT).as_posix()
        if relative not in before:
            changed.append({'archivo':relative,'estado':'creado'})
        elif digest(path)!=before[relative]:
            changed.append({'archivo':relative,'estado':'actualizado'})
    json_write(inventory_path,changed)
    facts=pd.read_csv(ROOT/'powerbi/geospatial/hechos_siniestros.csv')
    text='# Cierre técnico — MoviManrique45, versión cierre_v1\n\n'
    text+='Las cinco decisiones indicadas por el usuario quedan implementadas en el proceso, reportes, diccionario y datasets de Power BI. El cierre conserva el criterio espacial y los 604 IDs previamente contrastados con PostGIS.\n\n'
    text+='## Indicadores definitivos de esta versión\n\n'
    text+=table(facts.groupby('categoria_analisis').size().reset_index(name='registros'))
    text+='Total: **8332** registros de Comuna 3. Indicador principal: **604**, equivalentes al **7.25%** del total nominal. Los 40 de sensibilidad y cuatro externos pendientes no se suman al principal. No se presentan tasas de riesgo. El conjunto por proximidad (644) se conserva únicamente como comparación metodológica.\n\n'
    text+='## Decisiones implementadas\n\n'
    text+='1. Corredor principal: mismo buffer de 50 m recortado a Manrique, mismo predicado y mismos 604 IDs. Una lista de referencia de la versión detiene el proceso si cambian los IDs, incluso si el conteo permanece igual.\n'
    text+='2. Sensibilidad: los 40 puntos externos de Aranjuez a <=0.01 m del límite y <=50 m del eje reciben categoria_analisis=sensibilidad_borde. La tolerancia solo clasifica: no modifica el límite, coordenadas ni indicador.\n'
    text+='3. Cuatro externos restantes: categoria_analisis=revision_territorial y pendiente_revision_territorial=true. Se conserva su ubicación nominal de origen y se añade territorio_geometrico separado.\n'
    text+='4. Seis fragmentos: conservados, sin eliminar ni fusionar. El CSV de revisión registra la decisión y su origen reproducible mediante recorte territorial; no acredita conectividad funcional.\n'
    text+='5. CRS RAW: en cada ejecución se contrasta etiqueta EPSG:9377 y bounds geográficos. Se conserva la discrepancia conocida, sin corregir el RAW. Un estado diferente detiene esta versión para revisión.\n\n'
    text+='Categorías mutuamente excluyentes; resto_manrique contiene 7684 registros. sin_posicion_validada se reserva para casos sin georreferenciación válida (cero actualmente). [Diccionario](diccionario_datos.md) y [guía Power BI](powerbi.md).\n\n'
    text+='## Verificaciones ejecutadas\n\n'
    text+=f"Pruebas: **{tests['tests']} aprobadas**, {tests['failures']} fallos, {tests['errors']} errores. Se incluyen los 22 controles previos y ocho controles de cierre: partición, IDs exactos, rechazo de sustitución de ID con igual conteo, borde sin ampliación, relaciones/agregados, fragmentos intactos, discrepancia CRS y repetición de exportaciones.\n\n"
    text+=f"Dos ejecuciones sucesivas con las mismas fuentes, configuración y código: reproducible={manifest['reproducible']}. Se compararon hashes lógicos de geometrías/tablas y bytes de {len(manifest['export_hashes'])} CSV/GeoJSON. Fuentes originales intactas: {manifest['sources_unchanged']}; verificación SHA-256 incluida en pruebas. No se exige igualdad binaria de los GeoPackage por sus metadatos internos.\n\n"
    text+=f"QGIS existente reabierto tras actualizar capas derivadas: {qgis['layer_count']} capas válidas, proyecto sin cambios={qgis['project_unchanged']}. La comprobación SQL utiliza la evidencia previamente autenticada de solo lectura; en este cierre no se abrió una nueva conexión ni se modificaron tablas.\n\n"
    text+='Evidencia: [pruebas](../reports/geospatial/final_tests.txt), [manifiesto](../reports/geospatial/run.json), [CRS](../reports/geospatial/crs_raw_cierre.json), [QGIS](../reports/geospatial/qgis_final.json).\n\n'
    text+='## Archivos creados o modificados en este cierre\n\n'
    text+='Lista comparada por SHA-256 con el inventario anterior al cierre. Incluye derivados regenerados y archivos locales excluidos de Git; los RAW no fueron reescritos. Las rutas se indican respecto a la raíz del proyecto.\n\n'
    for row in changed:
        relative=row['archivo']
        text+=f"- {row['estado']}: `{relative}`\n"
    text+='\n## Revisión humana que permanece\n\n'
    text+='- Examinar los cuatro registros externos (125795, 140908, 154532 y 192142) con fuentes territoriales autorizadas. No reclasificarlos automáticamente.\n'
    text+='- Revisar la función vial de los seis fragmentos. La conservación en esta versión está decidida; cualquier corrección futura necesita aprobación.\n'
    text+='- Evaluar precisión posicional y tratamiento del borde para una versión futura. Los 40 actuales permanecen en sensibilidad, no en el principal.\n'
    text+='- Resolver el metadato CRS de la malla en una futura ingesta/documentación de la fuente, conservando siempre el RAW actual y su trazabilidad.\n'
    text+='- Importación y diseño de visualizaciones en Power BI cuando se solicite; no se alteraron dashboards.\n\n'
    text+='No se ejecutaron commits ni push. No se inició frontend ni backend. No hubo correcciones geométricas automáticas.\n'
    report_path.write_text(text,encoding='utf-8')
    print(f'Cierre: {tests["tests"]} pruebas, {len(changed)} archivos creados/actualizados; indicador principal 604.')

if __name__=='__main__':
    main()
