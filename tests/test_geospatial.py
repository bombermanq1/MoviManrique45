import json
import unittest
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point, box
from src.geospatial.common import ROOT, OUTPUT, metric, write_gpkg
from src.geospatial.geometry import audit
from src.geospatial.incidents import coordinate_mask, prepare, aggregate_grid

CONFIG = json.loads((ROOT/'src/geospatial/config.json').read_text())

class GeometryTests(unittest.TestCase):
    def test_crs_required(self):
        with self.assertRaises(ValueError):
            metric(gpd.GeoDataFrame(geometry=[Point(0,0)]))

    def test_metric_transform(self):
        frame = metric(gpd.GeoDataFrame(geometry=[Point(-75.56,6.28)], crs=4326))
        self.assertEqual(frame.crs.to_epsg(),9377)
        back = frame.to_crs(4326).geometry.iloc[0]
        self.assertAlmostEqual(back.x,-75.56,places=8)

    def test_tiny_connection_and_gap(self):
        roads = gpd.GeoDataFrame({'objectid':[1,2,3,4]}, geometry=[
            LineString([(0,0),(1,0)]), LineString([(1,0),(1.1,0)]),
            LineString([(1.1,0),(2,0)]), LineString([(10,0),(10.1,0)])], crs=9377)
        original = roads.geometry.to_wkb().tolist()
        _, parts, ends, gaps, _ = audit(roads, CONFIG)
        self.assertEqual(parts.loc[parts.objectid.eq(2),'clasificacion'].iloc[0], 'Posible conexion valida')
        self.assertEqual(parts.loc[parts.objectid.eq(4),'clasificacion'].iloc[0], 'Requiere revision manual')
        self.assertEqual(len(ends),8)
        self.assertGreater(len(gaps),0)
        self.assertEqual(original, roads.geometry.to_wkb().tolist())

    def test_no_source_write(self):
        with self.assertRaises(ValueError):
            write_gpkg(ROOT/'data/raw/test.gpkg', {})

    def test_invalid_coordinate_values(self):
        df = pd.DataFrame({'longitud':[-75,None,181,float('inf'),0], 'latitud':[6,6,6,6,91]})
        self.assertEqual(coordinate_mask(df)[2].tolist(), [True,False,False,False,False])

    def test_duplicate_ids_block(self):
        df = pd.read_csv(ROOT/'data/processed/siniestros_comuna3.csv', nrows=1)
        with self.assertRaises(ValueError):
            prepare(pd.concat([df,df]))

    def test_grid_boundary_unique(self):
        df = gpd.GeoDataFrame({'gravedad_siniestro':['HERIDOS']*3,'distancia_carrera45_m':[0,10,120]},
                             geometry=[Point(0,0),Point(100,0),Point(100,100)],crs=9377)
        points,zones,_ = aggregate_grid(df,box(-1,-1,201,201),100,.9)
        self.assertEqual(zones.cantidad.sum(),3)
        self.assertEqual(points.zona_id.nunique(),3)

class ProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT/'reports/geospatial/run.json').read_text(encoding='utf-8'))

    def test_source_integrity(self):
        from src.geospatial.probe import digest
        for path, expected in self.manifest['source_hashes'].items():
            self.assertEqual(digest(Path(path)),expected,path)

    def test_original_geometries(self):
        original=gpd.read_file(ROOT/'data/processed/carrera45_manrique.geojson').sort_values('objectid')
        reference=gpd.read_file(OUTPUT/'carrera45_auditoria.gpkg',layer='referencia').sort_values('objectid')
        self.assertEqual(original.geometry.to_wkb().tolist(),reference.geometry.to_wkb().tolist())

    def test_tiny_fragments_regression(self):
        tiny=gpd.read_file(OUTPUT/'carrera45_auditoria.gpkg',layer='fragmentos')
        self.assertEqual(len(tiny),6)
        self.assertEqual(set(tiny.objectid),{28471,20909,7611,24568})
        self.assertTrue(tiny.length.lt(1).all())

    def test_conservation_and_relations(self):
        facts=pd.read_csv(ROOT/'powerbi/geospatial/hechos_siniestros.csv')
        roads=pd.read_csv(ROOT/'powerbi/geospatial/segmentos.csv')
        zones=pd.read_csv(ROOT/'powerbi/geospatial/zonas.csv')
        self.assertEqual(len(facts),8332)
        self.assertTrue(facts.evento_id.is_unique)
        self.assertTrue(set(facts.segmento_cercano_id.dropna()) <= set(roads.segmento_cercano_id))
        self.assertTrue(set(facts.zona_id.dropna()) <= set(zones.zona_id))
        self.assertEqual(int(facts.dentro_manrique.sum()),int(zones.cantidad.sum()))

    def test_corridor_matches_existing_ids(self):
        points=gpd.read_file(OUTPUT/'siniestros_analisis.gpkg',layer='siniestros')
        selected=points.loc[points.dentro_corredor_50m.astype(bool)]
        previous=pd.read_csv(ROOT/'data/processed/siniestros_carrera45_50m.csv')
        self.assertEqual(set(selected.evento_id.astype(int)),set(previous.objectid))
        self.assertTrue(selected.distancia_carrera45_m.le(50+1e-6).all())

    def test_all_layers_valid(self):
        import pyogrio
        for name in ['carrera45_auditoria','siniestros_analisis']:
            for layer,_ in pyogrio.list_layers(OUTPUT/f'{name}.gpkg'):
                df=gpd.read_file(OUTPUT/f'{name}.gpkg',layer=layer)
                self.assertEqual(df.crs.to_epsg(),9377)
                self.assertTrue(df.geometry.is_valid.all(),layer)
                self.assertFalse(df.geometry.is_empty.any(),layer)

    def test_web_coordinates_and_privacy(self):
        for path in (OUTPUT/'web').glob('*.geojson'):
            df=gpd.read_file(path)
            self.assertEqual(df.crs.to_epsg(),4326)
            self.assertTrue(df.is_valid.all())
            xmin,ymin,xmax,ymax=df.total_bounds
            self.assertTrue(-76<xmin<=xmax<-75 and 6<ymin<=ymax<7)
            self.assertFalse({'direccion','radicado','evento_id'} & set(df.columns))

    def test_reproducibility(self):
        self.assertTrue(self.manifest['repeated_same_inputs'])
        self.assertTrue(self.manifest['reproducible'])

if __name__ == '__main__':
    unittest.main()
