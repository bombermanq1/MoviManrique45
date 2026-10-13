"""Analisis descriptivo de registros, no tasas de riesgo ni atribucion vial."""
import math
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box
from .common import ROOT, OUTPUT, REPORTS, metric, require_columns, valid_geometry, write_gpkg, table
from .closure_policy import classify, validate_frozen_ids

def coordinate_mask(frame):
    lon = pd.to_numeric(frame.longitud, errors='coerce')
    lat = pd.to_numeric(frame.latitud, errors='coerce')
    return lon, lat, lon.between(-180, 180) & lat.between(-90, 90)

def prepare(frame):
    require_columns(frame, ['objectid', 'fecha_siniestro', 'anio', 'longitud', 'latitud',
                            'clase_siniestro', 'gravedad_siniestro', 'barrio', 'num_comuna'])
    frame = frame.copy()
    if frame.objectid.isna().any() or frame.objectid.duplicated().any():
        raise ValueError('IDs de siniestro nulos/duplicados; resolver antes de agregar eventos.')
    frame['evento_id'] = frame.objectid.astype(str)
    lon, lat, mask = coordinate_mask(frame)
    dates = pd.to_datetime(frame.fecha_siniestro, format='%Y-%m-%d', errors='coerce')
    frame['fecha_valida'] = dates.notna()
    frame['anio_fuente'] = frame.anio
    frame['anio'] = dates.dt.year.astype('Int64')
    frame['mes_numero'] = dates.dt.month.astype('Int64')
    frame['coordenada_valida'] = mask
    for col in ['clase_siniestro', 'gravedad_siniestro', 'barrio']:
        frame[col] = frame[col].astype('string').str.strip().replace('', pd.NA).fillna('SIN INFORMACION')
    stats = dict(registros=len(frame), coordenadas_invalidas=int((~mask).sum()),
        fechas_invalidas=int(dates.isna().sum()),
        anio_discrepante=int((pd.to_numeric(frame.anio_fuente, errors='coerce') != frame.anio).fillna(True).sum()),
        duplicados_fila=int(frame.drop(columns=['evento_id']).duplicated().sum()),
        radicados_repetidos=int(frame.radicado.dropna().duplicated().sum()) if 'radicado' in frame else None,
        coincidencias_fecha_coordenada=int(frame.duplicated(['fecha_siniestro', 'latitud', 'longitud'], keep=False).sum()),
        categorias_nulas={c:int(frame[c].eq('SIN INFORMACION').sum()) for c in ['clase_siniestro','gravedad_siniestro','barrio']})
    # No georeference invalid rows; retain them in the nonspatial fact table.
    points = gpd.GeoDataFrame(frame.loc[mask].copy(), geometry=gpd.points_from_xy(lon[mask], lat[mask]), crs=4326)
    return frame, points, stats

def aggregate_grid(points, commune, size, quantile):
    points = points.copy()
    ix = np.floor(points.geometry.x / size).astype('int64')
    iy = np.floor(points.geometry.y / size).astype('int64')
    points['zona_id'] = ix.astype(str) + '_' + iy.astype(str)
    rows = []
    for zone, group in points.groupby('zona_id', sort=True):
        x, y = (int(n) for n in zone.split('_'))
        geom = box(x*size, y*size, (x+1)*size, (y+1)*size).intersection(commune)
        rows.append(dict(zona_id=zone, cantidad=len(group),
            heridos=int(group.gravedad_siniestro.eq('HERIDOS').sum()),
            muertos=int(group.gravedad_siniestro.eq('MUERTOS').sum()),
            cerca_100m=int(group.distancia_carrera45_m.le(100).sum()), geometry=geom))
    zones = gpd.GeoDataFrame(rows, columns=['zona_id','cantidad','heridos','muertos','cerca_100m','geometry'], crs=points.crs)
    threshold = float(zones.cantidad.quantile(quantile)) if len(zones) else math.inf
    zones['prioritaria'] = zones.cantidad.ge(threshold) & zones.cerca_100m.gt(0)
    return points, zones, threshold

def run(config, roads):
    raw = pd.read_csv(ROOT / 'data/raw/siniestros_medellin.csv')
    require_columns(raw, ['num_comuna'])
    source = raw.loc[raw.num_comuna.astype('string').str.strip().eq('Comuna 3')].copy()
    original = pd.read_csv(ROOT / 'data/processed/siniestros_comuna3.csv')
    if set(source.objectid) != set(original.objectid):
        raise ValueError('El filtro RAW no reproduce los IDs de Comuna 3 existentes.')
    facts, points, stats = prepare(source)
    stats['raw_total'] = len(raw)
    stats['ids_comuna_reproducidos'] = True
    all_communes = metric(gpd.read_file(ROOT / 'data/raw/comunas_medellin.geojson'))
    commune_frame = all_communes
    commune_frame = commune_frame.loc[commune_frame.codigo.astype(str).str.zfill(2).eq('03')].copy()
    if len(commune_frame) != 1 or not valid_geometry(commune_frame).all():
        raise ValueError('Limite de Comuna 3 ausente, ambiguo o invalido.')
    commune = commune_frame.geometry.union_all()
    # World-valid coordinates far outside Colombia cannot safely be projected with this CRS.
    geographic_extent = commune_frame.to_crs(4326).total_bounds
    local_mask = (points.geometry.x.between(geographic_extent[0]-0.1, geographic_extent[2]+0.1)
                  & points.geometry.y.between(geographic_extent[1]-0.1, geographic_extent[3]+0.1))
    stats['fuera_entorno_local'] = int((~local_mask).sum())
    points = metric(points.loc[local_mask], config['metric_crs'])
    if not valid_geometry(roads).all():
        raise ValueError('No se analizan distancias contra un eje invalido.')
    union = roads.geometry.union_all()
    points['distancia_carrera45_m'] = points.distance(union)
    points['dentro_manrique'] = points.geometry.intersects(commune)
    stats['fuera_limite_manrique'] = int((~points.dentro_manrique).sum())
    ordered_roads = roads.sort_values('objectid')
    # Tie-break is deterministic: smallest objectid. Nearest does not mean attribution.
    distances = np.column_stack([points.distance(g).to_numpy() for g in ordered_roads.geometry])
    points['segmento_cercano_id'] = ordered_roads.objectid.to_numpy()[distances.argmin(axis=1)]
    corridor = union.buffer(50).intersection(commune)
    points['dentro_corredor_50m'] = points.geometry.intersects(corridor)
    aranjuez=all_communes.loc[all_communes.codigo.astype(str).str.zfill(2).eq('04')]
    if len(aranjuez)!=1 or not valid_geometry(aranjuez).all():
        raise ValueError('Limite de Aranjuez ausente o invalido.')
    points=classify(points,commune,aranjuez.geometry.union_all(),config['boundary_sensitivity_m'])
    for i,row in points.loc[points.categoria_analisis.eq('revision_territorial')].iterrows():
        matches=all_communes.loc[all_communes.intersects(row.geometry)]
        points.loc[i,'territorio_geometrico']='; '.join(matches.codigo.astype(str)+':'+matches.nombre.astype(str)) or 'sin_coincidencia'
    validate_frozen_ids(points)
    comparison = []
    for distance in config['proximity_distances_m']:
        within = points.distancia_carrera45_m.le(distance + 1e-6)
        comparison.append(dict(distancia_m=distance, proximidad=int(within.sum()),
                               proximidad_en_manrique=int((within & points.dentro_manrique).sum())))
    previous = pd.read_csv(ROOT / 'data/processed/siniestros_carrera45_50m.csv')
    current_ids = set(points.loc[points.dentro_corredor_50m, 'objectid'])
    old_ids = set(previous.objectid)
    stats.update(corredor_50m=len(current_ids), corredor_previo=len(old_ids),
        ids_solo_actual=len(current_ids-old_ids), ids_solo_previo=len(old_ids-current_ids),
        fecha_min=str(pd.to_datetime(facts.fecha_siniestro, errors='coerce').min().date()),
        fecha_max=str(pd.to_datetime(facts.fecha_siniestro, errors='coerce').max().date()))
    in_commune, zones, threshold = aggregate_grid(points.loc[points.dentro_manrique], commune,
        config['grid_size_m'], config['priority_quantile'])
    points = points.merge(in_commune[['evento_id','zona_id']], on='evento_id', how='left', validate='one_to_one')
    stats.update(celdas_ocupadas=len(zones), umbral_prioridad=threshold, zonas_prioritarias=int(zones.prioritaria.sum()))
    spatial_cols = ['evento_id','distancia_carrera45_m','dentro_manrique','dentro_corredor_50m','segmento_cercano_id','zona_id']
    closure_cols=['categoria_analisis','es_indicador_principal','sensibilidad_borde',
        'pendiente_revision_territorial','distancia_limite_manrique_m','territorio_geometrico']
    spatial_cols+=closure_cols
    facts = facts.merge(points[spatial_cols], on='evento_id', how='left', validate='one_to_one')
    facts['categoria_analisis']=facts.categoria_analisis.fillna('sin_posicion_validada')
    for col in ['es_indicador_principal','sensibilidad_borde','pendiente_revision_territorial']:
        facts[col]=facts[col].fillna(False).astype(bool)
    stats['categorias_cierre']=facts.categoria_analisis.value_counts().to_dict()
    # Data minimization: no radicado, address or exact time in consumer datasets.
    keep = ['evento_id','anio','mes_numero','clase_siniestro','gravedad_siniestro','barrio',
        'num_comuna','fecha_valida','coordenada_valida','distancia_carrera45_m','dentro_manrique',
        'dentro_corredor_50m','segmento_cercano_id','zona_id']
    keep+=closure_cols
    facts = facts[keep]
    public_points = points[[c for c in keep if c in points] + ['geometry']].copy()
    layers = dict(siniestros=public_points, concentraciones=zones, zonas_prioritarias=zones.loc[zones.prioritaria].copy(),
                  corredor_50m=gpd.GeoDataFrame({'distancia_m':[50]}, geometry=[corridor], crs=roads.crs),
                  manrique=commune_frame[['codigo','nombre','geometry']])
    write_gpkg(OUTPUT / 'siniestros_analisis.gpkg', layers)
    sensitivity = pd.DataFrame(comparison)
    sensitivity.to_csv(OUTPUT / 'sensibilidad_distancias.csv', index=False)
    stats['sensibilidad'] = comparison
    report = '# Fase 3 — Analisis espacial de siniestros\n\n'
    report+='Cierre v1 aprobado: 604 IDs estrictos como indicador principal; 40 en sensibilidad al borde sin sumarlos al principal; cuatro externos en revision territorial. Categorias mutuamente excluyentes. El umbral de 0.01 m identifica sensibilidad, no ensancha el corredor.\n\n'
    report+=table(facts.groupby('categoria_analisis').size().reset_index(name='cantidad'))
    report += table(pd.DataFrame([(k,v) for k,v in stats.items() if not isinstance(v,(dict,list))],columns=['indicador','valor']))
    report += '\n## Sensibilidad a la distancia\n\n' + table(sensitivity)
    for column in ['anio','gravedad_siniestro','clase_siniestro']:
        report += f'\n## Distribucion por {column}\n\n'
        report += table(facts.groupby(column,dropna=False).size().reset_index(name='cantidad'))
    report += '\nFiltro reproducido desde RAW por num_comuna=Comuna 3. No se eliminan duplicados por radicado o por fecha/coordenada: no bastan para demostrar un mismo evento. objectid es obligatorio y unico.\n\n'
    report += 'Se valida fecha ISO, concordancia del año, categorias, rango mundial de coordenadas y entorno local (envolvente de Manrique ampliada 0.1 grados). Coordenadas fuera del entorno no se proyectan: permanecen en tabla de hechos con campos espaciales nulos. Coordenadas validas no garantizan exactitud del geocodificado.\n\n'
    report += 'Distancias EPSG:9377 a la union del eje, tolerancia numerica 0.000001 m. Corredor: buffer Shapely de 50 m recortado al limite oficial; incluye borde. La aproximacion poligonal del arco del buffer puede diferir de distancia<=50 en el limite.\n\n'
    report += f'Concentraciones: cuadricula fija de {config["grid_size_m"]} m anclada en (0,0) del CRS, recortada a Manrique; solo celdas ocupadas. Cada punto pertenece a una celda por floor(x/tamaño), floor(y/tamaño). Prioridad exploratoria: cantidad >= percentil {100*config["priority_quantile"]}% de celdas ocupadas (umbral {threshold}) y al menos un registro a <=100 m del eje. Empates incluidos.\n\n'
    report += 'No son hotspots estadisticamente significativos, causalidad, atribucion de via ni tasas de riesgo. Faltan exposicion, aforos y poblacion comparable. Variaciones anuales pueden reflejar cobertura o reporte; no equivalen a cambios del riesgo. No se presupone que 2025 sea un año completo.\n\n'
    report += 'Pruebas de fase: unicidad, filtro RAW, IDs congelados del cierre, relectura de capas/CRS. PostgreSQL fue contrastado en la validacion final previa; este cierre no reabre la base. Ver [validacion SQL](geospatial/validacion_final.md) y [cierre](geospatial/cierre_tecnico.md).\n'
    (REPORTS / 'analisis_espacial_siniestros.md').write_text(report, encoding='utf-8')
    return layers, facts, stats
