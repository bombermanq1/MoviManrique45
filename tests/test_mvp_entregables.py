"""Comprueba que los entregables reproducibles del MVP estén presentes."""

import json
from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[1]


class EntregablesMVPTests(unittest.TestCase):
    def test_archivos_mvp_presentes(self) -> None:
        rutas = [
            "web/index.html", "web/data/dashboard.json", "powerbi/implementation/consultas_powerquery.m",
            "powerbi/implementation/medidas.dax", "reports/ia_exploratoria.md",
            "deliverables/documento_tecnico.md", "deliverables/manual_ejecucion.md",
        ]
        for ruta in rutas:
            self.assertTrue((RAIZ / ruta).is_file(), ruta)

    def test_exportacion_web_conserva_total(self) -> None:
        datos = json.loads((RAIZ / "web/data/dashboard.json").read_text(encoding="utf-8"))
        self.assertEqual(datos["metadatos"]["registros"], 8332)
        self.assertEqual(len(datos["eventos"]), 8332)
