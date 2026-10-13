"""Auditoria por entidad y por parte, sin reparar ni fusionar fuentes."""
from itertools import combinations
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
from .common import ROOT, OUTPUT, REPORTS, metric, require_columns, valid_geometry, write_gpkg, table

def audit(eje, config):
    eje = metric(eje, config['metric_crs']).copy()
    require_columns(eje, ['objectid'])
    if eje.objectid.isna().any() or eje.objectid.duplicated().any():
        raise ValueError('objectid vial debe ser unico y no nulo.')
    eje['longitud_m'] = eje.length
    eje['valida'] = valid_geometry(eje)
    eje['duplicada'] = eje.geometry.normalize().to_wkb().duplicated(keep=False)
    rows = []
    for _, row in eje.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        parts = list(geom.geoms) if geom.geom_type == 'MultiLineString' else [geom]
        for number, part in enumerate(parts, 1):
            if part.geom_type != 'LineString':
                raise ValueError('El eje contiene geometria no lineal.')
            rows.append(dict(parte_id=f'{int(row.objectid)}:{number}', objectid=int(row.objectid),
                             parte=number, longitud_m=part.length, geometry=part))
    parts = gpd.GeoDataFrame(rows, crs=eje.crs)
    parts['diminuta'] = parts.longitud_m < config['tiny_length_m']
    endpoints, edges, relations = [], [], []
    tolerance = min(config['endpoint_tolerances_m'])
    for i, row in parts.iterrows():
        other = parts.loc[parts.index != i]
        for side, coord in enumerate([row.geometry.coords[0], row.geometry.coords[-1]]):
            point = Point(coord)
            distances = other.distance(point)
            nearest_idx = distances.idxmin() if len(distances) else None
            dist = float(distances.min()) if len(distances) else None
            neighbor = other.loc[nearest_idx] if nearest_idx is not None else None
            target = neighbor.geometry.interpolate(neighbor.geometry.project(point)) if neighbor is not None else point
            record = dict(extremo_id=f'{row.parte_id}:{side}', parte_id=row.parte_id,
                          objectid=row.objectid, lado=side, distancia_vecino_m=dist,
                          vecino_parte=neighbor.parte_id if neighbor is not None else '', geometry=point)
            for tol in config['endpoint_tolerances_m']:
                record[f'conexiones_{str(tol).replace(".", "_")}m'] = int((distances <= tol).sum())
            endpoints.append(record)
            if dist is not None and dist > tolerance:
                edges.append(dict(parte_id=row.parte_id, vecino_parte=neighbor.parte_id,
                                  distancia_m=dist, geometry=LineString([point, target])))
    ends = gpd.GeoDataFrame(endpoints, crs=eje.crs)
    classifications = []
    for _, part in parts.iterrows():
        ds = ends.loc[ends.parte_id.eq(part.parte_id), 'distancia_vecino_m']
        if not part.geometry.is_valid or not part.geometry.is_simple or part.geometry.length == 0:
            label = 'Posible error geometrico'
        elif ds.notna().all() and (ds <= tolerance).all():
            label = 'Posible conexion valida'
        else:
            label = 'Requiere revision manual'
        classifications.append(label)
    parts['clasificacion'] = classifications
    for i, j in combinations(parts.index, 2):
        a, b = parts.loc[i], parts.loc[j]
        distance = a.geometry.distance(b.geometry)
        if distance <= max(config['endpoint_tolerances_m']):
            intersection = a.geometry.intersection(b.geometry)
            relations.append(dict(parte_a=a.parte_id, parte_b=b.parte_id, distancia_m=distance,
                interseccion_tipo=intersection.geom_type if not intersection.is_empty else 'sin contacto',
                solape_m=intersection.length, cruza=a.geometry.crosses(b.geometry)))
    gaps = gpd.GeoDataFrame(edges, columns=['parte_id', 'vecino_parte', 'distancia_m', 'geometry'], crs=eje.crs)
    return eje, parts, ends, gaps, pd.DataFrame(relations)

def run(config):
    source = gpd.read_file(ROOT / 'data/processed/carrera45_manrique.geojson')
    eje, parts, ends, gaps, relations = audit(source, config)
    tiny = parts.loc[parts.diminuta].copy()
    tiny['decision_version']='conservar_sin_eliminar_ni_fusionar'
    tiny['origen_documentado']='reproducible_por_recorte_territorial'
    OUTPUT.mkdir(parents=True, exist_ok=True)
    relations.to_csv(OUTPUT / 'relaciones_partes.csv', index=False)
    write_gpkg(OUTPUT / 'carrera45_auditoria.gpkg', dict(referencia=source, segmentos=eje,
        partes=parts, fragmentos=tiny, extremos=ends, discontinuidades=gaps))
    review = __import__('pathlib').Path.home() / 'Documents/carrera45_revision.gpkg'
    comparison = 'GeoPackage externo no disponible.'
    if review.exists():
        ref = metric(gpd.read_file(review, layer='carrera45_segmentos')).set_index('objectid')
        local = eje.set_index('objectid')
        same_ids = set(ref.index) == set(local.index)
        equal = sum(local.loc[k].geometry.equals(ref.loc[k].geometry) for k in local.index if k in ref.index)
        comparison = f'GeoPackage de revision: mismos IDs={same_ids}; geometria topologicamente igual en {equal}/{len(local)} entidades.'
    summary = dict(segmentos=len(eje), partes=len(parts), fragmentos=len(tiny), longitud_m=float(eje.length.sum()),
                   invalidas=int((~eje.valida).sum()), duplicadas=int(eje.duplicada.sum()), candidatos_discontinuidad=len(gaps))
    report = '# Fase 2 — Auditoria geometrica Carrera 45\n\n' + table(pd.DataFrame(summary.items(),columns=['indicador','valor'])) + '\n'
    report += 'Se conserva cada geometria original. Se separan partes exclusivamente en una capa derivada. EPSG:9377, metros.\n\n'
    report += f'Tolerancias extremo-a-linea: {config["endpoint_tolerances_m"]} m. La clasificacion usa {min(config["endpoint_tolerances_m"])} m; no demuestra conectividad vial funcional. '
    report += 'Ambos extremos a esa tolerancia de otra parte: posible conexion valida; invalidez/no simplicidad/longitud cero: posible error; resto: revision manual. Incluye partes del mismo objectid.\n\n'
    report += table(tiny.drop(columns='geometry')) + '\n' + table(ends.loc[ends.parte_id.isin(tiny.parte_id)].drop(columns='geometry'))
    report += '\nLos candidatos de discontinuidad unen cada extremo sin contacto tolerado a su linea mas cercana. No son correcciones propuestas: pueden ser limites legitimos, ramales o cortes del recorte territorial. Las relaciones documentan cruces y solapes entre todas las partes cercanas.\n\n'
    report += comparison + '\n\nEl reporte anterior de continuidad usa 27 entidades preliminares; este analiza las 26 definitivas. La validacion final previa confirmo coincidencia exacta con PostgreSQL y reproduccion de los seis fragmentos por recorte territorial.\n\n'
    report += 'Decision de cierre v1: conservar los seis fragmentos sin eliminar ni fusionar. Reproducibilidad del recorte no demuestra conectividad vial funcional. Ver [contraste](geospatial/validacion_final_fragmentos.md). Pruebas: relectura exacta de geometria/CRS y conteos. Permanece la revision humana funcional; no la decision de conservacion en esta version.\n'
    (REPORTS / 'auditoria_geometrica_carrera45.md').write_text(report, encoding='utf-8')
    return {'segmentos': eje, 'partes': parts, 'fragmentos': tiny, 'extremos': ends, 'discontinuidades': gaps}, summary
