"""Reabre el QGZ existente sin guardarlo ni regenerar capas."""
import json
import os
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import QgsApplication,QgsProject,QgsMapSettings,QgsMapRendererParallelJob
from qgis.PyQt.QtCore import QSize
ROOT=Path(__file__).resolve().parents[2]

def main():
    import hashlib
    project_path=ROOT/'qgis/MoviManrique45_Analisis.qgz'
    before=hashlib.sha256(project_path.read_bytes()).hexdigest()
    app=QgsApplication([],False); app.initQgis()
    project=QgsProject()
    opened=project.read(str(project_path))
    layers=project.layerTreeRoot().checkedLayers()
    details=[]
    for layer in project.mapLayers().values():
        source=layer.source()
        path=Path(source.split('|')[0])
        details.append(dict(name=layer.name(),valid=layer.isValid(),features=layer.featureCount(),
            crs=layer.crs().authid(),source=source,source_exists=path.is_file(),read_only=layer.readOnly()))
    settings=QgsMapSettings(); settings.setLayers(layers)
    settings.setDestinationCrs(project.crs())
    settings.setExtent(project.viewSettings().defaultViewExtent())
    settings.setOutputSize(QSize(900,900))
    job=QgsMapRendererParallelJob(settings); job.start(); job.waitForFinished()
    errors=[str(e.message) for e in job.errors()]
    preview=ROOT/'reports/geospatial/qgis_final_preview.png'
    rendered=job.renderedImage().save(str(preview))
    result=dict(opened=opened,layer_count=len(details),layers=details,render_saved=rendered,render_errors=errors,
        project_unchanged=before==hashlib.sha256(project_path.read_bytes()).hexdigest())
    result['passed']=opened and len(details)==10 and all(l['valid'] and l['source_exists'] for l in details) and rendered and not errors
    (ROOT/'reports/geospatial/qgis_final.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=True),flush=True)
    settings.setLayers([]); layers.clear(); del job,settings,layer
    project.clear(); del project; app.exitQgis()

if __name__=='__main__':
    main()
