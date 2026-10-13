"""Inspeccion local y PostgreSQL estrictamente de solo lectura."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    import geopandas as gpd
    import pandas as pd
    import pyogrio
    import psycopg
    result = {'python': sys.version, 'dependencies': {}, 'files': {}, 'database': {}}
    for name in ['pandas', 'geopandas', 'shapely', 'pyproj', 'pyogrio', 'sqlalchemy', 'psycopg']:
        result['dependencies'][name] = importlib.import_module(name).__version__
    paths = sorted((ROOT / 'data/raw').glob('*')) + sorted((ROOT / 'data/processed').glob('*'))
    review = Path.home() / 'Documents/carrera45_revision.gpkg'
    if review.exists():
        paths.append(review)
    for path in paths:
        if not path.is_file() or path.name == '.gitkeep':
            continue
        item = {'sha256': digest(path), 'bytes': path.stat().st_size}
        if path.suffix == '.csv':
            df = pd.read_csv(path)
            item.update(rows=len(df), columns=list(df.columns), duplicate_rows=int(df.duplicated().sum()))
            if 'anio' in df:
                item['years'] = df.anio.value_counts(dropna=False).to_dict()
        elif path.suffix in ['.geojson', '.gpkg']:
            item['layers'] = {}
            for layer, _ in pyogrio.list_layers(path):
                df = gpd.read_file(path, layer=layer)
                item['layers'][layer] = dict(rows=len(df), columns=list(df.columns), crs=str(df.crs),
                    invalid=int((df.geometry.notna() & ~df.geometry.is_valid).sum()), empty=int(df.geometry.is_empty.sum()),
                    null=int(df.geometry.isna().sum()), types=df.geom_type.value_counts().to_dict())
        result['files'][str(path)] = item
    try:
        # libpq can use PGPASSWORD or an existing pgpass; never logs either.
        with psycopg.connect(host=os.getenv('PGHOST', 'localhost'), port=os.getenv('PGPORT', '5432'),
                dbname=os.getenv('PGDATABASE', 'movimanrique45'), user=os.getenv('PGUSER', 'postgres'),
                connect_timeout=5, options='-c default_transaction_read_only=on -c statement_timeout=15000') as conn:
            with conn.cursor() as cur:
                cur.execute('SHOW transaction_read_only')
                result['database']['read_only'] = cur.fetchone()[0]
                cur.execute('SELECT current_database(), version(), PostGIS_Full_Version()')
                result['database']['version'] = cur.fetchone()
                cur.execute("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('carrera45_segmentos','siniestros') ORDER BY table_name,ordinal_position")
                result['database']['columns'] = cur.fetchall()
                cur.execute("SELECT f_table_name,f_geometry_column,srid,type FROM geometry_columns WHERE f_table_schema='public' AND f_table_name IN ('carrera45_segmentos','siniestros')")
                result['database']['geometry_columns'] = cur.fetchall()
                for table in ['carrera45_segmentos', 'siniestros']:
                    cur.execute(psycopg.sql.SQL('SELECT count(*) FROM public.{}').format(psycopg.sql.Identifier(table)))
                    result['database'][table] = cur.fetchone()[0]
                for table, column, _, _ in result['database']['geometry_columns']:
                    cur.execute(psycopg.sql.SQL('SELECT ST_SRID({g}),count(*),count(*) FILTER (WHERE {g} IS NULL),count(*) FILTER (WHERE ST_IsEmpty({g})),count(*) FILTER (WHERE NOT ST_IsValid({g})) FROM public.{t} GROUP BY ST_SRID({g})').format(g=psycopg.sql.Identifier(column), t=psycopg.sql.Identifier(table)))
                    result['database'][table + '_geometry'] = cur.fetchall()
                result['database']['status'] = 'verified'
    except psycopg.Error as exc:
        result['database'] = {'status': 'blocked', 'error_type': type(exc).__name__,
            'reason': ('Contraseña requerida; no hay contraseña disponible para libpq.' if 'no password supplied' in str(exc)
                       else 'No se completo la conexion/consulta de solo lectura. Revisar autenticacion, servicio y esquema; no se registran credenciales.')}
        print('PostgreSQL:', type(exc).__name__, 'password_required=', 'no password supplied' in str(exc))
    output = ROOT / 'reports/geospatial'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'environment.json').write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=True, default=str))

if __name__ == '__main__':
    main()
