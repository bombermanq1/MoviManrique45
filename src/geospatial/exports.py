"""Productos para consumidores, con atributos explicitos y sin identificadores personales."""
import json
import pandas as pd
from .common import ROOT, json_write
from .closure_policy import category_dimension

def run(config, road_layers, incident_layers, facts):
    bi = ROOT / 'powerbi/geospatial'
    bi.mkdir(parents=True, exist_ok=True)
    facts.to_csv(bi / 'hechos_siniestros.csv', index=False, encoding='utf-8-sig')
    road_layers['segmentos'][['objectid','longitud_m','valida','duplicada']].rename(columns={'objectid':'segmento_cercano_id'}).to_csv(bi / 'segmentos.csv', index=False)
    zones = incident_layers['concentraciones']
    zones.drop(columns='geometry').to_csv(bi / 'zonas.csv', index=False)
    counts = {}
    for column in ['anio','gravedad_siniestro','clase_siniestro','barrio','dentro_corredor_50m','categoria_analisis']:
        summary = facts.groupby(column, dropna=False).size().reset_index(name='cantidad')
        summary.to_csv(bi / f'resumen_{column}.csv', index=False, encoding='utf-8-sig')
        counts[column] = int(summary.cantidad.sum())
    if any(value != len(facts) for value in counts.values()):
        raise ValueError('Totales de Power BI no conservan registros.')
    category_dimension().to_csv(bi/'categorias_analisis.csv',index=False,encoding='utf-8-sig')
    facts.groupby(['anio','categoria_analisis'],dropna=False).size().reset_index(name='cantidad').to_csv(bi/'resumen_anio_categoria.csv',index=False)
    road_layers['fragmentos'].drop(columns='geometry').to_csv(bi/'fragmentos_revision.csv',index=False,encoding='utf-8-sig')
    web = ROOT / 'data/processed/geospatial/web'
    web.mkdir(parents=True, exist_ok=True)
    selected = {
        'carrera45': road_layers['segmentos'][['objectid','longitud_m','geometry']],
        'fragmentos_revision': road_layers['fragmentos'][['parte_id','objectid','longitud_m','clasificacion','geometry']],
        'concentraciones': zones.loc[zones.cantidad.ge(config['web_min_count']), ['zona_id','cantidad','prioritaria','geometry']],
        'zonas_prioritarias': zones.loc[zones.prioritaria & zones.cantidad.ge(config['web_min_count']), ['zona_id','cantidad','prioritaria','geometry']]
    }
    manifest = {}
    for name, frame in selected.items():
        output = frame.to_crs(4326)
        path = web / f'{name}.geojson'
        # Keep full precision: rounding would collapse centimeter-scale fragments.
        path.write_text(output.to_json(drop_id=True, to_wgs84=True), encoding='utf-8')
        decoded = json.loads(path.read_text(encoding='utf-8'))
        if decoded['type'] != 'FeatureCollection' or len(decoded['features']) != len(frame):
            raise ValueError('GeoJSON no valido.')
        manifest[name] = dict(features=len(frame), bytes=path.stat().st_size, crs='EPSG:4326', columns=list(frame.columns))
    json_write(web / 'manifest.json', manifest)
    return {'powerbi_registros':len(facts), 'web':manifest}
