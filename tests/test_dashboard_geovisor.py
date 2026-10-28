"""Pruebas sin escritura para el contrato del dashboard estático y su geovisor."""

import json
from pathlib import Path
import unittest

from src.dashboard.datos import cargar_limite_manrique


RAIZ = Path(__file__).resolve().parents[1]


class DashboardGeovisorTests(unittest.TestCase):
    """Comprueba datos y controles declarados sin modificar productos fuente."""

    def test_payload_incluye_limite_oficial_y_cierre(self) -> None:
        payload = json.loads((RAIZ / "web" / "data" / "dashboard.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["eventos"]), 8332)
        self.assertEqual(len(payload["limite_manrique"]["features"]), 1)
        self.assertEqual(payload["limite_manrique"]["features"][0]["properties"]["codigo"], "03")
        self.assertEqual(payload["limite_manrique"]["features"][0]["properties"]["nombre"], "Manrique")
        conteos = {}
        for evento in payload["eventos"]:
            conteos[evento["categoria_analisis"]] = conteos.get(evento["categoria_analisis"], 0) + 1
        self.assertEqual(conteos, {
            "principal_50m": 604,
            "sensibilidad_borde": 40,
            "revision_territorial": 4,
            "resto_manrique": 7684,
        })

    def test_limite_leido_desde_raw_es_unico_y_poligonal(self) -> None:
        limite = cargar_limite_manrique()
        self.assertEqual(limite["type"], "FeatureCollection")
        self.assertEqual(len(limite["features"]), 1)
        self.assertIn(limite["features"][0]["geometry"]["type"], {"Polygon", "MultiPolygon"})

    def test_html_declara_interacciones_y_contexto(self) -> None:
        html = (RAIZ / "web" / "index.html").read_text(encoding="utf-8")
        javascript = "\n".join(ruta.read_text(encoding="utf-8") for ruta in (RAIZ / "web" / "js").glob("*.js"))
        requeridos = [
            "Cómo se construyó el análisis",
            "Qué permiten concluir estos datos",
            "layer-limite",
            "layer-eje",
            "layer-zonas",
            "layer-principal",
            "layer-borde",
            "layer-revision",
            "layer-resto",
            "map-zoom-in",
            "map-zoom-out",
            "pointerdown",
            "pointermove",
            "wheel",
            "seleccionarZona",
            "50 m no es una norma vial",
        ]
        for texto in requeridos:
            self.assertIn(texto, html + javascript)

    def test_mapa_usa_el_evento_de_teclado_recibido(self) -> None:
        javascript = (RAIZ / "web" / "js" / "mapa.js").read_text(encoding="utf-8")
        inicio = javascript.index("function manejarTeclado(evento)")
        fin = javascript.index("function enlazarMapa()", inicio)
        codigo = javascript[inicio:fin]
        self.assertIn("evento.key", codigo)
        self.assertIn("evento.preventDefault()", codigo)
        self.assertNotRegex(codigo, r"\bevent\.(?:key|target|preventDefault)\b")


if __name__ == "__main__":
    unittest.main()
