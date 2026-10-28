"""Comprueba que los recursos de la aplicación y su documentación existan."""

import json
from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[1]


class RecursosAplicacionTests(unittest.TestCase):
    def test_archivos_mvp_presentes(self) -> None:
        rutas = [
            "README.md", "web/css/styles.css", "web/js/app.js", "web/js/datos.js",
            "web/js/mapa.js", "web/js/intervenciones.js",
            "web/index.html", "web/data/dashboard.json", "powerbi/implementation/consultas_powerquery.m",
            "web/data/intervenciones.json", "src/dashboard/intervenciones.py",
            "powerbi/implementation/medidas.dax", "docs/datos.md",
            "docs/funcionamiento.md", "docs/instalacion.md",
        ]
        for ruta in rutas:
            self.assertTrue((RAIZ / ruta).is_file(), ruta)

    def test_exportacion_web_conserva_total(self) -> None:
        datos = json.loads((RAIZ / "web/data/dashboard.json").read_text(encoding="utf-8"))
        self.assertEqual(datos["metadatos"]["registros"], 8332)
        self.assertEqual(len(datos["eventos"]), 8332)
