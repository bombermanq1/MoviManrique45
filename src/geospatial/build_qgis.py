"""Ejecutar con bin/python-qgis-ltr.bat de QGIS, fuera del venv."""
import json
import os
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem,
    QgsLineSymbol, QgsMarkerSymbol, QgsFillSymbol, QgsSingleSymbolRenderer,
    QgsMapSettings, QgsMapRendererParallelJob, QgsRectangle,
    QgsGraduatedSymbolRenderer, QgsRendererRange, Qgis)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

ROOT = Path(__file__).resolve().parents[2]

def main():
    app = QgsApplication([], False)
    app.initQgis()
    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem('EPSG:9377'))
    project.setFilePathStorage(Qgis.FilePathType.Relative)
    folder = ROOT / 'qgis'
    folder.mkdir(exist_ok=True)
    path = folder / 'MoviManrique45_Analisis.qgz'
    project.setFileName(str(path))
    root = project.layerTreeRoot()
    definitions = [
        ('siniestros_analisis', 'manrique', 'Limite oficial de Manrique', 'fill', '#f4f1ea', True),
        ('siniestros_analisis', 'concentraciones', 'Concentraciones - celdas de 100 m', 'fill', '#f8dc9a', True),
        ('siniestros_analisis', 'zonas_prioritarias', 'Prioridad exploratoria - conteos altos', 'fill', '#f2a541', True),
        ('siniestros_analisis', 'corredor_50m', 'Corredor de 50 m recortado', 'fill', '#81d4db', True),
        ('carrera45_auditoria', 'referencia', 'Carrera 45 - referencia sin cambios', 'line', '#626b73', True),
        ('siniestros_analisis', 'siniestros', 'Siniestros Comuna 3 - proximidad, no atribucion', 'point', '#ad4056', True),
        ('carrera45_auditoria', 'segmentos', 'Carrera 45 - revision geometrica', 'line', '#176b9a', True),
        ('carrera45_auditoria', 'discontinuidades', 'Discontinuidades candidatas - revision manual', 'line', '#bd68bc', False),
        ('carrera45_auditoria', 'fragmentos', 'Fragmentos menores de 1 m', 'line', '#ff172d', True),
        ('carrera45_auditoria', 'extremos', 'Extremos para inspeccion de conexiones', 'point', '#ff172d', False),
    ]
    layers = []
    audit = []
    for package, name, title, kind, color, visible in definitions:
        uri = str(ROOT / f'data/processed/geospatial/{package}.gpkg') + '|layername=' + name
        layer = QgsVectorLayer(uri, title, 'ogr')
        if not layer.isValid() or layer.crs().authid() != 'EPSG:9377':
            raise RuntimeError(f'Capa invalida: {name}')
        if kind == 'line':
            symbol = QgsLineSymbol.createSimple({'line_color':color,'line_width':'0.65' if name == 'fragmentos' else '0.4'})
        elif kind == 'point':
            symbol = QgsMarkerSymbol.createSimple({'color':color,'size':'1.2','outline_style':'no'})
        else:
            symbol = QgsFillSymbol.createSimple({'color':color,'outline_color':'#aab5b8','outline_width':'0.12'})
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        if name == 'concentraciones':
            ranges = []
            for lower, upper, shade in [(0,10,'#fff3cf'),(10,25,'#f9d47b'),(25,50,'#efad42'),(50,100,'#d77926'),(100,1000000,'#994a1f')]:
                fill = QgsFillSymbol.createSimple({'color':shade,'outline_color':'#c4bba8','outline_width':'0.1'})
                ranges.append(QgsRendererRange(lower,upper,fill,f'{lower:g}–{upper:g} registros'))
            layer.setRenderer(QgsGraduatedSymbolRenderer('cantidad', ranges))
        layer.setReadOnly(True)
        if name == 'corredor_50m':
            layer.setOpacity(0.45)
        project.addMapLayer(layer)
        root.findLayer(layer.id()).setItemVisibilityChecked(visible)
        if visible:
            layers.insert(0, layer)
        audit.append({'name':name,'features':layer.featureCount(),'valid':layer.isValid(),'crs':layer.crs().authid()})
    extent = QgsRectangle(project.mapLayersByName('Limite oficial de Manrique')[0].extent())
    extent.scale(1.08)
    from qgis.core import QgsReferencedRectangle
    project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent, project.crs()))
    project.setTitle('MoviManrique45 - analisis geoespacial descriptivo')
    if not project.write():
        raise RuntimeError('No se pudo guardar el proyecto.')
    settings = QgsMapSettings()
    settings.setDestinationCrs(project.crs())
    settings.setLayers(layers)
    settings.setExtent(extent)
    settings.setOutputSize(QSize(1100, 1100))
    settings.setBackgroundColor(QColor('white'))
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    if job.errors():
        raise RuntimeError('Error de render QGIS: ' + str(job.errors()))
    preview = ROOT / 'reports/geospatial/qgis_preview.png'
    if not job.renderedImage().save(str(preview)):
        raise RuntimeError('No se guardo la previsualizacion.')
    check = QgsProject()
    if not check.read(str(path)) or any(not l.isValid() for l in check.mapLayers().values()):
        raise RuntimeError('Fallo reabriendo proyecto QGIS.')
    report = {'qgis_version':Qgis.QGIS_VERSION, 'project_reopened':True, 'layers':audit,
              'relative_paths':True, 'render_errors':0, 'preview':str(preview.relative_to(ROOT))}
    (ROOT / 'reports/geospatial/qgis_validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
    # Release providers before shutting down QGIS/GDAL on Windows.
    check.clear()
    settings.setLayers([])
    layers.clear()
    del job, settings, layer, symbol
    project.clear()
    del check
    app.exitQgis()

if __name__ == '__main__':
    main()
