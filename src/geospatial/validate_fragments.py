"""Contraste local de partes diminutas con malla vial y limite original."""
import json
from pathlib import Path
import geopandas as gpd
import pandas as pd
from .common import ROOT,OUTPUT,DOCS,table

def main():
    tiny=gpd.read_file(OUTPUT/'carrera45_auditoria.gpkg',layer='fragmentos')
    roads=gpd.read_file(ROOT/'data/processed/carrera45_manrique.geojson').set_index('objectid')
    network=gpd.read_file(ROOT/'data/raw/malla_vial_medellin.geojson')
    # Reproduce the explicitly documented interpretation in crear_carrera45_manrique.py.
    # This is a temporary in-memory comparison, never a rewrite of RAW.
    bounds=network.total_bounds
    if not (-76 < bounds[0] < bounds[2] < -75 and 6 < bounds[1] < bounds[3] < 7):
        raise ValueError('RAW no coincide con las coordenadas geograficas documentadas; revisar CRS manualmente.')
    network=network.set_crs(4326,allow_override=True).to_crs(9377).set_index('objectid')
    commune=gpd.read_file(ROOT/'data/raw/comunas_medellin.geojson')
    polygon=commune.loc[commune.codigo.astype(str).str.zfill(2).eq('03')].geometry.union_all()
    ends=gpd.read_file(OUTPUT/'carrera45_auditoria.gpkg',layer='extremos')
    review_path=Path.home()/'Documents/carrera45_revision.gpkg'
    review=gpd.read_file(review_path,layer='carrera45_segmentos').set_index('objectid') if review_path.exists() else None
    rows=[]
    for _,r in tiny.iterrows():
        raw=network.loc[r.objectid].geometry
        clipped=raw.intersection(polygon)
        siblings=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]
        distances=ends.loc[ends.parte_id.eq(r.parte_id),'distancia_vecino_m'].tolist()
        rows.append(dict(parte_id=r.parte_id,objectid=int(r.objectid),longitud_m=r.geometry.length,
            extremo_inicio_a_vecino_m=distances[0],extremo_final_a_vecino_m=distances[1],
            distancia_al_limite_m=r.geometry.distance(polygon.boundary),
            coincide_parte_recorte_raw=any(r.geometry.equals(p) for p in siblings),
            hausdorff_recorte_entidad_m=clipped.hausdorff_distance(roads.loc[r.objectid].geometry),
            coincide_revision_entidad=review.loc[r.objectid].geometry.equals(roads.loc[r.objectid].geometry) if review is not None else None))
    frame=pd.DataFrame(rows)
    frame.to_csv(OUTPUT/'fragmentos_validacion_final.csv',index=False)
    (ROOT/'reports/geospatial/fragments_final.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    report='# Contraste final local de los seis fragmentos\n\n'+table(frame)
    report+='\nSe vuelve a intersectar en memoria la entidad correspondiente de la malla RAW con el límite oficial. Se contrasta cada parte diminuta contra ese resultado y la entidad definitiva contra el GeoPackage de revisión. No se guardan geometrías corregidas ni se modifica ninguna fuente.\n\n'
    report+='Advertencia de trazabilidad: la malla RAW declara EPSG:9377, pero sus bounds son '+str(bounds.tolist())+'. El script preexistente crear_carrera45_manrique.py documenta su interpretación como EPSG:4326 antes de proyectar. Se reproduce explícitamente esa interpretación solo en memoria para esta comprobación. Confiar literalmente en la etiqueta produciría intersecciones vacías. El inventario inicial verificó la etiqueta, no su coherencia numérica; queda rectificado.\n\n'
    report+='Una parte reproducible por el recorte territorial y tocando su borde es compatible con un efecto del recorte; no demuestra que sea una conexión vial válida ni autoriza eliminarla. Las distancias extremo-a-vecino explican la clasificación conservadora de revisión manual. El contraste con PostgreSQL se registra aparte.\n'
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS/'validacion_final_fragmentos.md').write_text(report,encoding='utf-8')
    print(frame.to_string(index=False))

if __name__=='__main__':
    main()
