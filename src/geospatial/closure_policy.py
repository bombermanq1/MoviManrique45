"""Decisiones de cierre v1: clasificacion derivada sin cambiar el indicador estricto."""
import json
import geopandas as gpd
import pandas as pd
from .common import ROOT, json_write

CATEGORIES = [
    ('principal_50m','Indicador principal: corredor estricto de 50 m',True,False),
    ('sensibilidad_borde','Sensibilidad al borde de Aranjuez; excluida del principal',False,False),
    ('revision_territorial','Registro externo pendiente de revision territorial',False,True),
    ('resto_manrique','Dentro de Manrique, fuera del corredor principal',False,False),
    ('sin_posicion_validada','Sin posicion apta para clasificacion espacial',False,True),
]

def check_raw_crs():
    path=ROOT/'data/raw/malla_vial_medellin.geojson'
    frame=gpd.read_file(path)
    bounds=frame.total_bounds.tolist()
    geographic=(-76<bounds[0]<bounds[2]<-75 and 6<bounds[1]<bounds[3]<7)
    known=frame.crs is not None and frame.crs.to_epsg()==9377 and geographic
    result={'file':'data/raw/malla_vial_medellin.geojson','declared_crs':str(frame.crs),'bounds':bounds,
        'coherent_declared_crs':False if known else None,
        'status':'discrepancia_conocida_preservada' if known else 'requiere_revision',
        'action':'RAW intacto. No se usa la etiqueta para medir; se conserva el eje EPSG:9377 validado.',
        'historical_interpretation':'EPSG:4326 en memoria documentado por crear_carrera45_manrique.py; no correccion persistente.'}
    json_write(ROOT/'reports/geospatial/crs_raw_cierre.json',result)
    if not known:
        raise ValueError('El CRS/bounds RAW cambio respecto al cierre v1; requiere revision explicita.')
    return result

def classify(points, commune, aranjuez, boundary_tolerance=.01):
    result=points.copy()
    result['distancia_limite_manrique_m']=result.distance(commune.boundary)
    result['territorio_geometrico']='03:Manrique'
    result.loc[~result.dentro_manrique,'territorio_geometrico']='externo'
    on_aranjuez=result.intersects(aranjuez)
    result.loc[~result.dentro_manrique & on_aranjuez,'territorio_geometrico']='04:Aranjuez'
    edge=(~result.dentro_manrique & on_aranjuez & result.distancia_limite_manrique_m.le(boundary_tolerance)
          & result.distancia_carrera45_m.le(50))
    result['categoria_analisis']='resto_manrique'
    result.loc[~result.dentro_manrique,'categoria_analisis']='revision_territorial'
    result.loc[edge,'categoria_analisis']='sensibilidad_borde'
    result.loc[result.dentro_corredor_50m,'categoria_analisis']='principal_50m'
    result['es_indicador_principal']=result.categoria_analisis.eq('principal_50m')
    result['sensibilidad_borde']=result.categoria_analisis.eq('sensibilidad_borde')
    result['pendiente_revision_territorial']=result.categoria_analisis.eq('revision_territorial')
    return result

def validate_frozen_ids(points):
    expected=json.loads((ROOT/'src/geospatial/ids_cierre_v1.json').read_text())
    for category,ids in expected.items():
        actual=set(points.loc[points.categoria_analisis.eq(category),'objectid'].astype(int))
        if actual != set(ids):
            raise ValueError(f'Cambian los IDs aprobados de {category}; detener y revisar antes de exportar.')

def category_dimension():
    return pd.DataFrame(CATEGORIES,columns=['categoria_analisis','descripcion','incluye_indicador_principal','requiere_revision_territorial'])
