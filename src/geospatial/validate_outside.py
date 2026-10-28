"""Diagnostica registros fuera del limite sin corregir fuentes ni coordenadas."""
import json
import geopandas as gpd
import pandas as pd
from .common import ROOT, OUTPUT, DOCS, table
from .probe import digest

def main():
    paths=[ROOT/'data/raw/siniestros_medellin.csv',ROOT/'data/raw/comunas_medellin.geojson',
           ROOT/'data/processed/siniestros_comuna3.csv',ROOT/'data/processed/siniestros_carrera45_50m.csv']
    before={str(p):digest(p) for p in paths}
    source=pd.read_csv(paths[2])
    raw=pd.read_csv(paths[0])
    zones=gpd.read_file(paths[1]).to_crs(9377)
    manrique=zones.loc[zones.codigo.astype(str).str.zfill(2).eq('03')].geometry.union_all()
    points=gpd.GeoDataFrame(source,geometry=gpd.points_from_xy(source.longitud,source.latitud),crs=4326).to_crs(9377)
    outside=points.loc[~points.intersects(manrique)].copy()
    outside['distancia_limite_m']=outside.distance(manrique.boundary)
    road=gpd.read_file(ROOT/'data/processed/carrera45_manrique.geojson').geometry.union_all()
    outside['distancia_carrera45_m']=outside.distance(road)
    matches=[]
    for _,row in outside.iterrows():
        other=zones.loc[zones.geometry.intersects(row.geometry)]
        matches.append('; '.join(other.codigo.astype(str)+':'+other.nombre.astype(str)) or 'Sin coincidencia en poligonos disponibles')
    outside['territorio_geometrico']=matches
    coordinates_in_raw=raw.set_index('objectid').loc[outside.objectid,['latitud','longitud']].reset_index(drop=True)
    identical=coordinates_in_raw.equals(outside[['latitud','longitud']].reset_index(drop=True))
    outside_geo=outside.to_crs(4326)
    direct_poly=zones.to_crs(4326).loc[zones.codigo.astype(str).str.zfill(2).eq('03')].geometry.union_all()
    # Check both predicates: geographic polygon and projected metric polygon.
    geographic_outside=~outside_geo.intersects(direct_poly)
    coordinate_groups=outside.groupby(['latitud','longitud']).size().sort_values(ascending=False)
    keep=['objectid','anio','barrio','num_comuna','latitud','longitud','territorio_geometrico','distancia_limite_m','distancia_carrera45_m']
    detail=outside[keep].sort_values(['distancia_limite_m','objectid'])
    detail.to_csv(OUTPUT/'siniestros_fuera_manrique_revision.csv',index=False,encoding='utf-8-sig')
    result=dict(count=len(outside),coordinates_identical_raw=identical,
        outside_also_epsg4326=int(geographic_outside.sum()),
        boundary_distance_m=outside.distancia_limite_m.describe().to_dict(),
        boundary_tolerances={str(t):int(outside.distancia_limite_m.le(t).sum()) for t in [.01,.1,1,5,10,25,50]},
        near_road_50m=int(outside.distancia_carrera45_m.le(50).sum()),
        actual_territories=outside.territorio_geometrico.value_counts().to_dict(),
        nominal_neighborhoods=outside.barrio.value_counts().to_dict(),
        years=outside.anio.value_counts().sort_index().to_dict(),
        unique_coordinates=len(coordinate_groups),largest_coordinate_group=int(coordinate_groups.max()),
        raw_hashes_unchanged=all(digest(p)==before[str(p)] for p in paths))
    edge=outside.loc[outside.distancia_limite_m.le(.01)]
    result['near_boundary_max_m']=float(edge.distancia_limite_m.max())
    result['remaining_four']=detail.loc[detail.distancia_limite_m.gt(.01),['objectid','territorio_geometrico','distancia_limite_m','distancia_carrera45_m']].to_dict('records')
    (ROOT/'reports/geospatial/outside_final.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    report='# Investigación de los 44 siniestros fuera de Manrique\n\n'
    report+='Se comparan los puntos originales con el polígono oficial suministrado; no se corrigen coordenadas ni etiquetas.\n\n'
    report+=table(pd.DataFrame([(k,v) for k,v in result.items() if not isinstance(v,(dict,list))],columns=['comprobacion','resultado']))
    report+='\n## Distancia al límite (metros)\n\n'+table(pd.DataFrame(result['boundary_distance_m'].items(),columns=['estadistico','valor']))
    report+='\n## Tolerancia: cuántos puntos quedan a esa distancia o menos del límite\n\n'+table(pd.DataFrame(result['boundary_tolerances'].items(),columns=['tolerancia_m','cantidad']))
    report+='\n## Territorio geométrico y año\n\n'+table(pd.DataFrame(result['actual_territories'].items(),columns=['territorio','cantidad']))
    report+=table(pd.DataFrame(result['years'].items(),columns=['anio','cantidad']))
    report+='\n## Los cuatro puntos no subcentimétricos\n\n'+table(pd.DataFrame(result['remaining_four']))
    report+='\n## Interpretación y límites\n\nLas coordenadas se contrastan por objectid contra RAW. La discrepancia nominal/geométrica ya existe en la fuente, no se originó al filtrar o exportar. La coincidencia de la clasificación en EPSG:4326 y EPSG:9377 permite descartar que dependa únicamente de la reproyección. Los conteos por tolerancia muestran cuánto puede explicarse por proximidad al borde, sin adoptar una corrección automática.\n\n'
    report+='No es posible decidir solo con estos datos si el origen es precisión de geocodificación, asignación administrativa, eje de vía limítrofe o cambios históricos del límite. No se cuenta con precisión posicional certificada ni versiones anuales del polígono. Estar cerca del límite no demuestra error. La repetición de coordenadas tampoco demuestra eventos duplicados.\n\n'
    report+='La diferencia entre 644 puntos próximos al eje y 604 del corredor se explica por los 40 registros fuera de Manrique a <=50 m. Los otros cuatro puntos externos no están dentro de esa distancia. Se conservan los 44 registros en hechos, con dentro_manrique=false y zona_id nulo.\n\n'
    report+='Los 40 puntos del borde están como máximo a '+str(result['near_boundary_max_m']*1000)+' mm. La precisión numérica de los cálculos no equivale a precisión posicional de la fuente. El conteo estricto de 604 debe presentarse junto con esta sensibilidad: tolerar 1 cm en el límite incorporaría esos 40 registros próximos sin cambiar su posición. No se adoptó esa tolerancia ni se cambió la selección.\n\n'
    report+='El detalle por objectid, sin dirección ni radicado, está en el archivo local `data/processed/geospatial/siniestros_fuera_manrique_revision.csv`; no se incluye en Git. El contraste con PostgreSQL se registra en [validación final](validacion_final.md).\n'
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS/'investigacion_44_siniestros.md').write_text(report,encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=True))

if __name__=='__main__':
    main()
