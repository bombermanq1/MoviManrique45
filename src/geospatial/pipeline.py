"""Ejecutar: python -m src.geospatial.pipeline; salidas derivadas deterministas."""
import argparse
import json
import logging
from pathlib import Path
from . import geometry, incidents, exports
from .common import ROOT, REPORTS, frame_digest, json_write
from .probe import digest
from .closure_policy import check_raw_crs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT / 'src/geospatial/config.json')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    if config.get('release')!='cierre_v1' or config.get('boundary_sensitivity_m')!=.01:
        raise ValueError('El cierre v1 conserva la sensibilidad de 1 cm sin cambiar el indicador estricto.')
    if config['metric_crs'] != 9377 or config['grid_size_m'] <= 0 or not 0 < config['priority_quantile'] < 1:
        raise ValueError('Configuracion invalida para el dominio del proyecto.')
    if not config['endpoint_tolerances_m'] or min(config['endpoint_tolerances_m']) <= 0:
        raise ValueError('Tolerancias deben ser positivas.')
    if config['tiny_length_m'] <= 0 or config['web_min_count'] < 1 or any(d<=0 for d in config['proximity_distances_m']):
        raise ValueError('Umbrales invalidos.')
    report_dir = REPORTS / 'geospatial'
    report_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=report_dir / 'pipeline.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s', force=True)
    paths = sorted((ROOT/'data/raw').glob('*')) + sorted((ROOT/'data/processed').glob('*'))
    review = Path.home()/'Documents/carrera45_revision.gpkg'
    if review.exists():
        paths.append(review)
    before = {str(p):digest(p) for p in paths if p.is_file()}
    code_hashes={p.name:digest(p) for p in sorted((ROOT/'src/geospatial').iterdir()) if p.suffix in ['.py','.json']}
    try:
        crs_check=check_raw_crs()
        logging.warning('RAW: etiqueta CRS incoherente con coordenadas; discrepancia conocida conservada sin cambiar fuente.')
        logging.info('Inicio de auditoria geometrica')
        roads, road_stats = geometry.run(config)
        logging.info('Inicio de analisis de siniestros')
        layers, facts, incident_stats = incidents.run(config, roads['segmentos'])
        export_stats = exports.run(config, roads, layers, facts)
        fingerprints = {f'roads/{k}':frame_digest(v) for k,v in roads.items()}
        fingerprints.update({f'incidents/{k}':frame_digest(v) for k,v in layers.items()})
        fingerprints['facts'] = frame_digest(facts)
        export_hashes={str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'powerbi/geospatial').glob('*.csv'))}
        export_hashes.update({str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'data/processed/geospatial/web').glob('*.geojson'))})
        manifest_path = report_dir/'run.json'
        previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
        same_inputs = previous is not None and previous['source_hashes'] == before and previous['config'] == config and previous.get('code_hashes')==code_hashes
        reproducible = (fingerprints == previous['logical_hashes'] and export_hashes==previous.get('export_hashes')) if same_inputs else None
        unchanged = all(digest(Path(p)) == h for p,h in before.items())
        if not unchanged:
            raise RuntimeError('Una fuente cambio durante la ejecucion.')
        result = dict(config=config, source_hashes=before, sources_unchanged=unchanged,
            code_hashes=code_hashes,export_hashes=export_hashes,crs_check=crs_check,
            logical_hashes=fingerprints, repeated_same_inputs=same_inputs, reproducible=reproducible,
            roads=road_stats, incidents=incident_stats, exports=export_stats)
        json_write(manifest_path, result)
        if reproducible is False:
            raise RuntimeError('Resultados distintos con fuentes y configuracion iguales.')
        logging.info('Finalizado; fuentes intactas=%s; reproducible=%s', unchanged, reproducible)
        print(json.dumps({k:v for k,v in result.items() if k not in ['source_hashes','logical_hashes','code_hashes','export_hashes']}, indent=2, ensure_ascii=True))
    except Exception:
        logging.exception('Ejecucion incompleta; revisar productos de las fases antes de consumirlos')
        raise

if __name__ == '__main__':
    main()
