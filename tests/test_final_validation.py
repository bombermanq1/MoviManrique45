import json
import unittest
from src.geospatial.common import ROOT

def report(name):
    return json.loads((ROOT/'reports/geospatial'/name).read_text(encoding='utf-8'))

class FinalValidationTests(unittest.TestCase):
    def test_connection_read_only(self):
        db=report('database_final.json')
        self.assertEqual(db['status'],'validated_available_tables')
        self.assertEqual(db['read_only'],'on')

    def test_26_geometries_identical(self):
        roads=report('database_final.json')['tables']['carrera45_segmentos']
        self.assertEqual(roads['rows'],26)
        self.assertEqual(len(roads['comparison']),26)
        self.assertTrue(all(r['exact_coordinates'] and r['hausdorff_m']==0 for r in roads['comparison']))

    def test_six_parts_reproduced(self):
        db=report('database_final.json')['tables']['carrera45_segmentos']['tiny_parts']
        self.assertEqual(len(db),6)
        self.assertTrue(all(len(r['equal_local_parts'])==1 for r in db))
        local=report('fragments_final.json')
        self.assertTrue(all(r['coincide_parte_recorte_raw'] and r['hausdorff_recorte_entidad_m']==0 for r in local))

    def test_incident_ids_and_attributes(self):
        data=report('database_final.json')['tables']['siniestros']
        self.assertEqual(data['rows'],8332)
        self.assertEqual(data['corridor_50m_rows'],604)
        self.assertFalse(data['scope_ids_only_db'] or data['scope_ids_only_local'])
        self.assertFalse(data['corridor_ids_only_db'] or data['corridor_ids_only_local'])
        self.assertFalse(any(data['attribute_discrepancies'].values()))
        self.assertLess(data['max_longitude_delta_degrees'],1e-8)
        self.assertLess(data['max_latitude_delta_degrees'],1e-8)

    def test_native_postgis_corridor(self):
        sql=report('database_final.json')['tables']['siniestros']['postgis_native']
        self.assertEqual(sql['corridor_rows'],604)
        self.assertFalse(sql['ids_only_sql'] or sql['ids_only_local'])
        self.assertEqual(len(sql['outside_rows']),44)
        import pandas as pd
        local=pd.read_csv(ROOT/'data/processed/geospatial/siniestros_fuera_manrique_revision.csv')
        self.assertEqual({r['objectid'] for r in sql['outside_rows']},set(local.objectid))

    def test_boundary_investigation(self):
        data=report('outside_final.json')
        self.assertEqual(data['count'],44)
        self.assertEqual(data['boundary_tolerances']['0.01'],40)
        self.assertEqual(len(data['remaining_four']),4)
        self.assertTrue(data['coordinates_identical_raw'] and data['raw_hashes_unchanged'])

    def test_existing_qgis(self):
        data=report('qgis_final.json')
        self.assertTrue(data['passed'] and data['project_unchanged'])
        self.assertEqual(data['layer_count'],10)

if __name__=='__main__':
    unittest.main()
