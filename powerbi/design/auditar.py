"""Solo lectura de fuentes; guarda evidencia aquí y documentación en docs/."""
from pathlib import Path
import json
import hashlib
import pandas as pd
import geopandas as gpd

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
DOCS=ROOT/'docs'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    paths=sorted((ROOT/'powerbi/geospatial').glob('*.csv'))
    protected=paths+list((ROOT/'data/processed/geospatial').glob('*.gpkg'))+list((ROOT/'data/processed/geospatial/web').glob('*.geojson'))+[ROOT/'data/processed/siniestros_comuna3_limpios.csv']
    before={str(p.relative_to(ROOT)):sha(p) for p in protected}
    tables={p.stem:pd.read_csv(p) for p in paths}
    inventory={}
    for p in paths:
        df=tables[p.stem]
        inventory[p.name]={'rows':len(df),'bytes':p.stat().st_size,'sha256':sha(p),
            'columns':[{ 'name':c,'inferred_dtype':str(df[c].dtype),'nulls':int(df[c].isna().sum()),'distinct':int(df[c].nunique())} for c in df],
            'duplicate_rows':int(df.duplicated().sum())}
    facts=tables['hechos_siniestros']; zones=tables['zonas']; segments=tables['segmentos']
    counts=facts.categoria_analisis.value_counts().to_dict()
    expected=json.loads((ROOT/'src/geospatial/ids_cierre_v1.json').read_text())
    ids={k:set(facts.loc[facts.categoria_analisis.eq(k),'evento_id'])==set(v) for k,v in expected.items()}
    support=pd.read_csv(ROOT/'data/processed/siniestros_comuna3_limpios.csv',usecols=['objectid','fecha_siniestro','latitud','longitud'])
    dates=pd.to_datetime(support.fecha_siniestro,format='%Y-%m-%d',errors='coerce')
    joined=facts.merge(support,left_on='evento_id',right_on='objectid',how='left',validate='one_to_one')
    layers=gpd.read_file(ROOT/'data/processed/geospatial/siniestros_analisis.gpkg',layer='zonas_prioritarias')
    stats={'rows':len(facts),'unique_ids':facts.evento_id.is_unique,'categories':counts,'frozen_ids_equal':ids,
        'years':facts.groupby('anio').size().to_dict(),'months':len(facts[['anio','mes_numero']].drop_duplicates()),
        'severity':facts.gravedad_siniestro.value_counts().to_dict(),'types':facts.clase_siniestro.value_counts().to_dict(),
        'nominal_territories':int(facts[['num_comuna','barrio']].drop_duplicates().shape[0]),
        'geometric_territories':facts.territorio_geometrico.value_counts().to_dict(),
        'zones':len(zones),'zone_nulls':int(facts.zona_id.isna().sum()),'priority_zones':int(zones.prioritaria.sum()),
        'priority_zone_ids_match':set(zones.loc[zones.prioritaria,'zona_id'])==set(layers.zona_id),
        'zone_counts_equal':facts.loc[facts.zona_id.notna()].groupby('zona_id').size().sort_index().equals(zones.set_index('zona_id').cantidad.sort_index()),
        'segments':len(segments),'fragments':len(tables['fragmentos_revision']),
        'missing_zone_fk':sorted(set(facts.zona_id.dropna())-set(zones.zona_id)),
        'missing_segment_fk':sorted(set(facts.segmento_cercano_id.dropna())-set(segments.segmento_cercano_id)),
        'missing_category_fk':sorted(set(facts.categoria_analisis)-set(tables['categorias_analisis'].categoria_analisis)),
        'supplement':{'rows':len(support),'unique_ids':support.objectid.is_unique,'missing_join_dates':int(joined.fecha_siniestro.isna().sum()),
            'valid_coordinate_ranges':bool(support.latitud.between(-90,90).all() and support.longitud.between(-180,180).all()),
            'invalid_dates':int(dates.isna().sum()),'start':str(dates.min().date()),'end':str(dates.max().date()),
            'ids_equal':set(support.objectid)==set(facts.evento_id),
            'year_matches':bool(pd.to_datetime(joined.fecha_siniestro).dt.year.eq(joined.anio).all()),
            'month_matches':bool(pd.to_datetime(joined.fecha_siniestro).dt.month.eq(joined.mes_numero).all())},
        'principal_severity':facts.loc[facts.es_indicador_principal].gravedad_siniestro.value_counts().to_dict(),
        'principal_types':facts.loc[facts.es_indicador_principal].clase_siniestro.value_counts().to_dict(),
        'principal_by_year':facts.loc[facts.es_indicador_principal].groupby('anio').size().to_dict()}
    stats['dimension_keys_unique']={name:bool(tables[name][key].is_unique) for name,key in [('zonas','zona_id'),('segmentos','segmento_cercano_id'),('categorias_analisis','categoria_analisis'),('fragmentos_revision','parte_id')]}
    stats['geojson_inventory']={p.name:{'features':len(json.loads(p.read_text(encoding='utf-8'))['features']),'bytes':p.stat().st_size} for p in (ROOT/'data/processed/geospatial/web').glob('*.geojson')}
    stats['unchanged']=all(sha(ROOT/p)==h for p,h in before.items())
    (OUT/'auditoria.json').write_text(json.dumps({'inventory':inventory,'checks':stats,'protected_hashes':before},indent=2,ensure_ascii=False),encoding='utf-8')
    lines=['# Auditoría Power BI — solo lectura','', 'No se modificaron datasets ni se ejecutó el ETL geoespacial. Tipos inferidos con pandas; los tipos semánticos para Power BI se especifican en el diseño.','',
        '| CSV | Filas | Columnas | Duplicados completos |','|---|---:|---:|---:|']
    for name,info in inventory.items():
        lines.append(f'| [{name}](../powerbi/geospatial/{name}) | {info["rows"]} | {len(info["columns"])} | {info["duplicate_rows"]} |')
    lines+=['','## Comprobaciones','', '```json',json.dumps(stats,indent=2,ensure_ascii=False),'```','', '## Columnas y perfil real']
    for name,info in inventory.items():
        lines+=['',f'### {name}','','| Columna | Tipo inferido | Nulos | Distintos |','|---|---|---:|---:|']
        lines += [f'| {c["name"]} | {c["inferred_dtype"]} | {c["nulls"]} | {c["distinct"]} |' for c in info['columns']]
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS/'auditoria_powerbi.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(stats,indent=2,ensure_ascii=True))

if __name__=='__main__': main()
