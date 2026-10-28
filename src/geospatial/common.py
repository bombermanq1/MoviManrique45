"""Validaciones, escritura aislada y huellas reproducibles."""
import hashlib
import json
from pathlib import Path
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'data/processed/geospatial'
REPORTS = ROOT / 'reports'
DOCS = ROOT / 'docs'

def require_columns(frame, columns):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f'Faltan columnas: {sorted(missing)}')

def metric(frame, epsg=9377):
    if frame.crs is None:
        raise ValueError('CRS no declarado; no se asigna uno por suposicion.')
    result = frame.to_crs(epsg)
    if not result.crs.is_projected or any(a.unit_name != 'metre' for a in result.crs.axis_info):
        raise ValueError('CRS de medida no metrico.')
    return result

def valid_geometry(frame):
    return frame.geometry.notna() & ~frame.geometry.is_empty & frame.geometry.is_valid

def write_gpkg(path, layers):
    """Reemplaza solo el producto del modulo, nunca acumula filas entre ejecuciones."""
    path = Path(path).resolve()
    if path.parent != OUTPUT.resolve():
        raise ValueError('GeoPackage fuera de la carpeta derivada autorizada.')
    path.parent.mkdir(parents=True, exist_ok=True)
    # staging sibling: original completed product stays intact until all layers exist.
    tmp = path.with_name(path.stem + '.tmp.gpkg')
    if tmp.exists():
        raise FileExistsError(f'Revisar staging de ejecucion anterior: {tmp.name}')
    for name, frame in layers.items():
        frame.to_file(tmp, layer=name, driver='GPKG', engine='pyogrio', index=False,
                      geometry_type='Unknown', promote_to_multi=False)
    for name, frame in layers.items():
        reread = gpd.read_file(tmp, layer=name)
        if len(frame) != len(reread) or frame.crs != reread.crs:
            raise ValueError(f'Fallo de lectura posterior: {name}')
        if frame.geometry.to_wkb().tolist() != reread.geometry.to_wkb().tolist():
            raise ValueError(f'La serializacion altero la geometria: {name}')
    tmp.replace(path)

def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def table(frame):
    return '```text\n' + frame.to_string(index=False) + '\n```\n'

def frame_digest(frame):
    """Hash logico; independiente de timestamps internos de GeoPackage."""
    data = pd.DataFrame(frame.drop(columns='geometry', errors='ignore')).copy()
    if 'geometry' in frame:
        data['geometry_wkb'] = frame.geometry.to_wkb(hex=True)
    return hashlib.sha256(data.to_csv(index=False, lineterminator='\n').encode()).hexdigest()
