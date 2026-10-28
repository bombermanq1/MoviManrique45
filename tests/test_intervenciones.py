"""Pruebas del módulo de propuestas sin modificar datos oficiales."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import unittest

import geopandas as gpd

from src.dashboard.datos import cargar_hechos, validar_cierre
from src.dashboard.intervenciones import CATALOGO_INTERVENCIONES, construir_payload_intervenciones


RAIZ = Path(__file__).resolve().parents[1]


class IntervencionesTests(unittest.TestCase):
    """Comprueba fichas reales, métricas conciliadas y propuestas no ejecutadas."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = construir_payload_intervenciones()
        cls.dashboard = json.loads((RAIZ / "web" / "data" / "dashboard.json").read_text(encoding="utf-8"))

    def test_las_doce_zonas_reales_tienen_ficha(self) -> None:
        zonas_capa = {
            str(feature["properties"]["zona_id"])
            for feature in self.dashboard["zonas_prioritarias"]["features"]
        }
        zonas_fichas = {ficha["zona_id"] for ficha in self.payload["zonas"]}
        self.assertEqual(len(zonas_capa), 12)
        self.assertEqual(zonas_fichas, zonas_capa)
        self.assertTrue(all(ficha["estado_evaluacion"] == "Pendiente de inspección" for ficha in self.payload["zonas"]))

    def test_los_indicadores_historicos_coinciden_con_los_eventos(self) -> None:
        conteos = Counter(
            str(evento["zona_id"])
            for evento in self.dashboard["eventos"]
            if evento["zona_id"] is not None
        )
        for ficha in self.payload["zonas"]:
            historico = ficha["diagnostico_historico"]
            self.assertEqual(historico["registros_historicos"], conteos[ficha["zona_id"]])
            self.assertEqual(sum(item["cantidad"] for item in historico["por_categoria_analisis"]), conteos[ficha["zona_id"]])
            self.assertEqual(sum(item["cantidad"] for item in historico["por_gravedad"]), conteos[ficha["zona_id"]])
            self.assertEqual(sum(item["cantidad"] for item in historico["por_tipo"]), conteos[ficha["zona_id"]])

    def test_catalogo_es_candidato_y_no_inventa_costos(self) -> None:
        catalogo_ids = {medida["id"] for medida in CATALOGO_INTERVENCIONES}
        self.assertEqual(len(catalogo_ids), 8)
        for ficha in self.payload["zonas"]:
            self.assertEqual(set(ficha["intervenciones_candidatas"]), catalogo_ids)
            self.assertEqual(ficha["costos_preliminares"]["estado"], "Pendiente de estudio técnico y presupuesto")
            self.assertIn("no es una puntuación de riesgo", ficha["comparacion_exploratoria"]["aclaracion"].lower())

    def test_los_segmentos_reportados_son_intersecciones_reales(self) -> None:
        zonas = gpd.read_file(RAIZ / "data" / "processed" / "geospatial" / "web" / "zonas_prioritarias.geojson")
        eje = gpd.read_file(RAIZ / "data" / "processed" / "geospatial" / "web" / "carrera45.geojson")
        for ficha in self.payload["zonas"]:
            zona = zonas.loc[zonas["zona_id"].astype(str).eq(ficha["zona_id"])].iloc[0]
            esperados = sorted(int(valor) for valor in eje.loc[eje.geometry.intersects(zona.geometry), "objectid"])
            self.assertEqual(ficha["evidencia_geoespacial"]["segmentos_eje_intersectados_objectid"], esperados)

    def test_el_cierre_original_permanece_intacto(self) -> None:
        resultado = validar_cierre(cargar_hechos())
        self.assertEqual(resultado["filas"], 8332)
        self.assertEqual(resultado["principal_50m"], 604)


class InterfazIntervencionesTests(unittest.TestCase):
    """Verifica el contrato declarativo del módulo web."""

    def test_html_declara_selector_ficha_y_mapa(self) -> None:
        html = (RAIZ / "web" / "index.html").read_text(encoding="utf-8")
        javascript = "\n".join(ruta.read_text(encoding="utf-8") for ruta in (RAIZ / "web" / "js").glob("*.js"))
        for texto in (
            "Posibles mejoras, zona por zona.",
            "zona-selector",
            "zona-ficha",
            "zona-comparacion",
            "intervenciones.json",
            "validarIntervenciones",
            "actualizarFichaIntervenciones",
            "Ver en el mapa",
            "Pendiente de inspección",
        ):
            self.assertIn(texto, html + javascript)


if __name__ == "__main__":
    unittest.main()
