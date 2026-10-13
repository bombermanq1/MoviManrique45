import json
import unittest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point,box
from src.geospatial.common import ROOT
from src.geospatial.closure_policy import classify,validate_frozen_ids

class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts=pd.read_csv(ROOT/'powerbi/geospatial/hechos_siniestros.csv')
        cls.ids=json.loads((ROOT/'src/geospatial/ids_cierre_v1.json').read_text())

    def test_exclusive_partition(self):
        counts=self.facts.categoria_analisis.value_counts().to_dict()
        self.assertEqual(counts,dict(principal_50m=604,sensibilidad_borde=40,revision_territorial=4,resto_manrique=7684))
        self.assertEqual(sum(counts.values()),8332)
        self.assertTrue(self.facts.evento_id.is_unique)

    def test_frozen_identity_and_flags(self):
        for category,ids in self.ids.items():
            self.assertEqual(set(self.facts.loc[self.facts.categoria_analisis.eq(category),'evento_id']),set(ids))
        self.assertTrue(self.facts.es_indicador_principal.equals(self.facts.dentro_corredor_50m))
        self.assertFalse((self.facts.es_indicador_principal & self.facts.sensibilidad_borde).any())
        self.assertEqual(self.facts.pendiente_revision_territorial.sum(),4)

    def test_identity_guard_rejects_same_count_replacement(self):
        altered=self.facts.rename(columns={'evento_id':'objectid'}).copy()
        idx=altered.index[altered.categoria_analisis.eq('principal_50m')][0]
        altered.loc[idx,'objectid']=-1
        with self.assertRaises(ValueError):
            validate_frozen_ids(altered)

    def test_border_never_expands_main_indicator(self):
        points=gpd.GeoDataFrame({'dentro_manrique':[False,False,True],
            'dentro_corredor_50m':[False,False,True],'distancia_carrera45_m':[2,2,2]},
            geometry=[Point(-.001,10),Point(-2,10),Point(2,10)],crs=9377)
        result=classify(points,box(0,0,100,100),box(-100,0,0,100))
        self.assertEqual(result.categoria_analisis.tolist(),['sensibilidad_borde','revision_territorial','principal_50m'])
        self.assertEqual(result.es_indicador_principal.tolist(),[False,False,True])

    def test_bi_dimension_and_rollups(self):
        folder=ROOT/'powerbi/geospatial'
        dim=pd.read_csv(folder/'categorias_analisis.csv')
        self.assertTrue(dim.categoria_analisis.is_unique)
        self.assertTrue(set(self.facts.categoria_analisis)<=set(dim.categoria_analisis))
        summary=pd.read_csv(folder/'resumen_anio_categoria.csv')
        actual=self.facts.groupby(['anio','categoria_analisis']).size().rename('cantidad').sort_index()
        pd.testing.assert_series_equal(summary.set_index(['anio','categoria_analisis']).cantidad.sort_index(),actual)

    def test_six_fragments_kept(self):
        bi=pd.read_csv(ROOT/'powerbi/geospatial/fragmentos_revision.csv')
        gpkg=gpd.read_file(ROOT/'data/processed/geospatial/carrera45_auditoria.gpkg',layer='fragmentos')
        source=gpd.read_file(ROOT/'data/processed/carrera45_manrique.geojson').set_index('objectid')
        self.assertEqual(len(bi),6)
        self.assertTrue(bi.decision_version.eq('conservar_sin_eliminar_ni_fusionar').all())
        for _,row in gpkg.iterrows():
            geom=source.loc[row.objectid].geometry
            parts=list(geom.geoms) if geom.geom_type=='MultiLineString' else [geom]
            part=parts[int(row.parte)-1]
            self.assertEqual(part.wkb,row.geometry.wkb)

    def test_crs_discrepancy_preserved(self):
        info=json.loads((ROOT/'reports/geospatial/crs_raw_cierre.json').read_text(encoding='utf-8'))
        self.assertEqual(info['declared_crs'],'EPSG:9377')
        self.assertFalse(info['coherent_declared_crs'])
        self.assertEqual(info['status'],'discrepancia_conocida_preservada')

    def test_repeat_includes_exports_and_code(self):
        info=json.loads((ROOT/'reports/geospatial/run.json').read_text(encoding='utf-8'))
        self.assertTrue(info['reproducible'])
        self.assertIn('closure_policy.py',info['code_hashes'])
        self.assertTrue(any('resumen_anio_categoria.csv' in p for p in info['export_hashes']))

if __name__=='__main__':
    unittest.main()
