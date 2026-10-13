"""Final read-only database validation. --interactive uses a masked local dialog."""
import argparse
import json
import os
from pathlib import Path
import re
import traceback
import geopandas as gpd
import pandas as pd
import psycopg
from psycopg import sql
from shapely import from_wkb

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/geospatial/database_final.json'

def save(result):
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding='utf-8')

def parameters():
    # Same local libpq configuration as probe.py and the existing ETL scripts.
    settings = dict(connect_timeout=5, options='-c default_transaction_read_only=on -c statement_timeout=30000')
    if not os.getenv('PGSERVICE'):
        settings.update(host=os.getenv('PGHOST','localhost'), port=os.getenv('PGPORT','5432'),
            dbname=os.getenv('PGDATABASE','movimanrique45'), user=os.getenv('PGUSER','postgres'))
    return settings

def safe_error(exc, password=None):
    message = str(exc)
    for value in [password, os.getenv('PGPASSWORD')]:
        if value:
            message = message.replace(value, '[REDACTED]')
    return re.sub(r'(?i)(password\s*=\s*)[^\s]+', r'\1[REDACTED]', message)

def inspect(conn):
    result = {'status':'connected', 'tables':{}}
    with conn.cursor() as cur:
        cur.execute('SHOW transaction_read_only')
        result['read_only'] = cur.fetchone()[0]
        if result['read_only'] != 'on':
            raise RuntimeError('Read-only guard failed')
        cur.execute('SELECT current_database(),version(),PostGIS_Full_Version()')
        result['versions'] = cur.fetchone()
        cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2")
        result['available_tables'] = cur.fetchall()
        cur.execute("SELECT f_table_schema,f_table_name,f_geometry_column,srid,type FROM geometry_columns")
        result['geometry_columns'] = cur.fetchall()
        for table in ['carrera45_segmentos','siniestros']:
            cur.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position",(table,))
            cols = cur.fetchall()
            if not cols:
                result['tables'][table] = {'status':'absent'}
                continue
            names = [c[0] for c in cols]
            cur.execute(sql.SQL('SELECT count(*) FROM public.{}').format(sql.Identifier(table)))
            info = {'columns':cols,'rows':cur.fetchone()[0]}
            result['tables'][table] = info
            geoms = [g for g in result['geometry_columns'] if g[0]=='public' and g[1]==table]
            info['geometries'] = geoms
            if table == 'carrera45_segmentos' and geoms and 'objectid' in names:
                geom = sql.Identifier(geoms[0][2])
                cur.execute(sql.SQL('SELECT objectid,ST_SRID({g}),ST_AsBinary({g}),ST_IsValid({g}),ST_IsEmpty({g}) FROM public.carrera45_segmentos ORDER BY objectid').format(g=geom))
                values = cur.fetchall()
                info['srids'] = sorted(set(v[1] for v in values if v[1] is not None))
                info['null_or_empty'] = sum(v[2] is None or v[4] for v in values)
                info['invalid_nonnull'] = sum(v[3] is False for v in values)
                if info['srids'] == [9377] and not info['null_or_empty']:
                    db = gpd.GeoDataFrame({'objectid':[v[0] for v in values]}, geometry=[from_wkb(bytes(v[2])) for v in values], crs=9377)
                    local = gpd.read_file(ROOT/'data/processed/carrera45_manrique.geojson')
                    info['duplicate_ids'] = int(db.objectid.duplicated().sum())
                    info['ids_only_db'] = sorted(set(db.objectid)-set(local.objectid))
                    info['ids_only_local'] = sorted(set(local.objectid)-set(db.objectid))
                    comparisons = []
                    if not info['duplicate_ids']:
                        reference = local.set_index('objectid')
                        for _,row in db.iterrows():
                            if row.objectid not in reference.index:
                                continue
                            original = reference.loc[row.objectid].geometry
                            comparisons.append(dict(objectid=row.objectid, topological_equal=row.geometry.equals(original),
                                exact_coordinates=row.geometry.equals_exact(original,0),
                                hausdorff_m=row.geometry.hausdorff_distance(original), length_delta_m=row.geometry.length-original.length))
                    info['comparison'] = comparisons
                cur.execute(sql.SQL('SELECT objectid,(d).path,ST_Length((d).geom),ST_AsBinary((d).geom) FROM (SELECT objectid,ST_Dump({g}) AS d FROM public.carrera45_segmentos) q WHERE ST_SRID((d).geom)=9377 AND ST_Length((d).geom)<1 ORDER BY objectid,(d).path').format(g=geom))
                tiny = cur.fetchall()
                local_tiny = gpd.read_file(ROOT/'data/processed/geospatial/carrera45_auditoria.gpkg',layer='fragmentos')
                info['tiny_parts'] = [dict(objectid=v[0],path=v[1],length_m=v[2],
                    equal_local_parts=[r.parte_id for _,r in local_tiny.loc[local_tiny.objectid.eq(v[0])].iterrows() if from_wkb(bytes(v[3])).equals(r.geometry)]) for v in tiny]
            if table == 'siniestros':
                # Fetch only technical fields, not addresses, radicado or other personal fields.
                allowed = [c for c in ['objectid','anio','num_comuna','latitud','longitud','fecha_siniestro','gravedad_siniestro','clase_siniestro'] if c in names]
                if allowed:
                    fields = [sql.Identifier(c) for c in allowed]
                    if geoms:
                        fields += [sql.SQL('ST_AsBinary({})').format(sql.Identifier(geoms[0][2])),sql.SQL('ST_SRID({})').format(sql.Identifier(geoms[0][2]))]
                    cur.execute(sql.SQL('SELECT {} FROM public.siniestros').format(sql.SQL(',').join(fields)))
                    values = cur.fetchall()
                    df = pd.DataFrame(values, columns=allowed+(['wkb','srid'] if geoms else []))
                    if 'objectid' in df:
                        info['duplicate_ids'] = int(df.objectid.duplicated().sum())
                        info['null_ids'] = int(df.objectid.isna().sum())
                    if 'num_comuna' in df:
                        info['territorial_counts'] = df.num_comuna.value_counts(dropna=False).to_dict()
                    if 'anio' in df:
                        info['years'] = df.anio.value_counts(dropna=False).to_dict()
                    scope = df.loc[df.num_comuna.astype(str).str.strip().eq('Comuna 3')].copy() if 'num_comuna' in df else df.copy()
                    info['analysis_scope'] = 'num_comuna=Comuna 3' if 'num_comuna' in df else 'entire available table; territorial label absent'
                    info['scope_rows'] = len(scope)
                    points = None
                    if geoms:
                        info['srids'] = scope.srid.value_counts(dropna=False).to_dict()
                        usable = scope.loc[scope.wkb.notna() & scope.srid.gt(0)].copy()
                        if usable.srid.nunique()==1:
                            points=gpd.GeoDataFrame(usable.drop(columns=['wkb','srid']),geometry=[from_wkb(bytes(v)) for v in usable.wkb],crs=int(usable.srid.iloc[0])).to_crs(9377)
                            info['coordinate_source']='database geometry'
                    elif {'latitud','longitud'} <= set(scope):
                        lon=pd.to_numeric(scope.longitud,errors='coerce'); lat=pd.to_numeric(scope.latitud,errors='coerce')
                        mask=lon.between(-76,-75)&lat.between(6,7)
                        points=gpd.GeoDataFrame(scope.loc[mask].copy(),geometry=gpd.points_from_xy(lon[mask],lat[mask]),crs=4326).to_crs(9377)
                        info['coordinate_source']='latitude/longitude attributes; EPSG:4326 per local source convention'
                    if points is not None:
                        valid=points.geometry.notna() & points.geometry.is_valid & ~points.geometry.is_empty & points.geom_type.eq('Point')
                        info['unusable_geometry_rows']=len(scope)-int(valid.sum())
                        points=points.loc[valid]
                        corridor=gpd.read_file(ROOT/'data/processed/geospatial/siniestros_analisis.gpkg',layer='corredor_50m').geometry.union_all()
                        selected=points.loc[points.intersects(corridor)]
                        info['corridor_50m_rows']=len(selected)
                        if 'objectid' in points:
                            previous=pd.read_csv(ROOT/'data/processed/siniestros_carrera45_50m.csv')
                            normalize=lambda values:set(pd.to_numeric(values,errors='raise').astype('int64'))
                            info['corridor_ids_only_db']=sorted(normalize(selected.objectid)-normalize(previous.objectid))
                            info['corridor_ids_only_local']=sorted(normalize(previous.objectid)-normalize(selected.objectid))
                            local=pd.read_csv(ROOT/'data/processed/siniestros_comuna3.csv')
                            info['scope_ids_only_db']=sorted(normalize(scope.objectid)-normalize(local.objectid))
                            info['scope_ids_only_local']=sorted(normalize(local.objectid)-normalize(scope.objectid))
                            if not info['duplicate_ids'] and not info['scope_ids_only_db'] and not info['scope_ids_only_local']:
                                aligned=points.set_index('objectid').sort_index().to_crs(4326)
                                local=local.set_index('objectid').sort_index()
                                info['max_longitude_delta_degrees']=float((aligned.geometry.x-local.longitud).abs().max())
                                info['max_latitude_delta_degrees']=float((aligned.geometry.y-local.latitud).abs().max())
                                info['attribute_discrepancies']={c:int((aligned[c].astype(str).str.strip()!=local[c].astype(str).str.strip()).sum()) for c in ['fecha_siniestro','gravedad_siniestro','clase_siniestro'] if c in aligned}
                        # Independent computation inside PostGIS, local polygon is a query parameter only.
                        if geoms and geoms[0][3]==4326 and 'objectid' in names and result['tables'].get('carrera45_segmentos',{}).get('srids')==[9377]:
                            commune=gpd.read_file(ROOT/'data/raw/comunas_medellin.geojson')
                            boundary=commune.loc[commune.codigo.astype(str).str.zfill(2).eq('03')].geometry.union_all()
                            road_column=result['tables']['carrera45_segmentos']['geometries'][0][2]
                            query=sql.SQL('''WITH territory AS (SELECT ST_GeomFromWKB(%s,9377) AS g),
                              road AS (SELECT ST_UnaryUnion(ST_Collect({road})) AS g FROM public.carrera45_segmentos),
                              corridor AS (SELECT ST_Intersection(ST_Buffer(road.g,50,'quad_segs=16'),territory.g) AS g FROM road,territory),
                              points AS (SELECT objectid,ST_Transform({geom},9377) AS g FROM public.siniestros)
                              SELECT points.objectid,ST_Intersects(points.g,corridor.g),ST_Intersects(points.g,territory.g),
                                ST_Distance(points.g,road.g),ST_Distance(points.g,ST_Boundary(territory.g))
                              FROM points,corridor,territory,road ORDER BY objectid''').format(road=sql.Identifier(road_column),geom=sql.Identifier(geoms[0][2]))
                            cur.execute(query,(boundary.wkb,))
                            checks=cur.fetchall()
                            native_ids={r[0] for r in checks if r[1]}
                            old_ids=set(pd.read_csv(ROOT/'data/processed/siniestros_carrera45_50m.csv').objectid)
                            info['postgis_native']={'scope':'all rows actually in public.siniestros',
                                'corridor_rows':len(native_ids),'ids_only_sql':sorted(native_ids-old_ids),'ids_only_local':sorted(old_ids-native_ids),
                                'proximity_50m_rows':sum(r[3]<=50 for r in checks),
                                'outside_rows':[{'objectid':r[0],'road_distance_m':r[3],'boundary_distance_m':r[4]} for r in checks if not r[2]],
                                'boundary_source':'local official polygon passed as WKB parameter; no database writes',
                                'buffer_quad_segs':16}
                    else:
                        info['spatial_validation']='blocked: no usable unambiguous geometry or coordinate schema'
        result['status']='validated_available_tables'
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--interactive',action='store_true')
    args=parser.parse_args()
    diagnosis={'configured_env':{k:bool(os.getenv(k)) for k in ['PGPASSWORD','PGPASSFILE','PGSERVICE','PGSERVICEFILE','PGHOST','PGUSER','PGDATABASE']},
        'default_pgpass_exists':(Path(os.getenv('APPDATA',''))/'postgresql/pgpass.conf').exists()}
    password=None
    try:
        conn=psycopg.connect(**parameters())
    except psycopg.Error as exc:
        diagnosis['initial_error']={'type':type(exc).__name__,'sqlstate':exc.sqlstate,'message':safe_error(exc)}
        if not args.interactive:
            save({'status':'blocked','diagnosis':diagnosis})
            print(json.dumps(diagnosis,ensure_ascii=True,indent=2))
            return
        import tkinter as tk
        from tkinter import simpledialog, messagebox
        root=tk.Tk(); root.withdraw(); root.attributes('-topmost',True)
        password=simpledialog.askstring('MoviManrique45 - validacion de solo lectura',
            'Contraseña PostgreSQL para la conexión existente (postgres, localhost:5432).\nSe usa solo en memoria; no se guarda ni se muestra.',show='*',parent=root)
        if password is None:
            save({'status':'cancelled','diagnosis':diagnosis}); root.destroy(); return
        try:
            conn=psycopg.connect(**parameters(),password=password)
        except psycopg.Error as login_error:
            save({'status':'blocked','diagnosis':diagnosis,'error':{'type':type(login_error).__name__,'sqlstate':login_error.sqlstate,'message':safe_error(login_error,password)}})
            password=None
            messagebox.showerror('Validacion PostgreSQL','La autenticacion fallo. El informe registra el error sin credenciales.',parent=root)
            root.destroy(); return
        password=None
        root.destroy()
    try:
        with conn:
            result=inspect(conn)
        result['diagnosis']=diagnosis
        save(result)
    except Exception as exc:
        save({'status':'query_failed','diagnosis':diagnosis,'error':{'type':type(exc).__name__,'message':safe_error(exc)}})

if __name__=='__main__':
    main()
