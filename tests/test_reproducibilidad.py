"""Controles del mecanismo local de demostración y sus insumos públicos."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.request import urlopen
import unittest


RAIZ = Path(__file__).resolve().parents[1]


class _ManejadorSilencioso(SimpleHTTPRequestHandler):
    """Evita ruido en consola durante la comprobación HTTP local."""

    def log_message(self, _format: str, *_args: object) -> None:
        return


class ReproducibilidadTests(unittest.TestCase):
    def test_requirements_son_utf8_y_declaran_las_dependencias_opcionales(self) -> None:
        base = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
        mvp = (RAIZ / "requirements_mvp.txt").read_text(encoding="utf-8")
        self.assertNotIn("\x00", base)
        for paquete in ("pandas==", "geopandas==", "requests==", "shapely=="):
            self.assertIn(paquete, base)
        self.assertIn("-r requirements.txt", mvp)
        for paquete in ("streamlit", "plotly", "pydeck"):
            self.assertIn(paquete, mvp)

    def test_iniciador_reproducible_contiene_validacion_y_servidor(self) -> None:
        ruta = RAIZ / "scripts" / "iniciar_demo.ps1"
        contenido = ruta.read_text(encoding="utf-8")
        self.assertIn("src.dashboard.exportar_web", contenido)
        self.assertIn("verificar_insumos_demo.py", contenido)
        self.assertIn("http.server", contenido)
        self.assertIn("--bind 127.0.0.1", contenido)
        self.assertIn("SoloExportar", contenido)

    def test_vista_web_declara_los_resultados_oficiales(self) -> None:
        payload = json.loads((RAIZ / "web" / "data" / "dashboard.json").read_text(encoding="utf-8"))
        eventos = payload["eventos"]
        conteos = {}
        for evento in eventos:
            categoria = evento["categoria_analisis"]
            conteos[categoria] = conteos.get(categoria, 0) + 1
        self.assertEqual(len(eventos), 8332)
        self.assertEqual(conteos, {
            "principal_50m": 604,
            "sensibilidad_borde": 40,
            "revision_territorial": 4,
            "resto_manrique": 7684,
        })
        self.assertEqual(len(payload["limite_manrique"]["features"]), 1)
        self.assertEqual(len(payload["carrera45"]["features"]), 26)
        self.assertEqual(len(payload["zonas_prioritarias"]["features"]), 12)

    def test_archivos_web_se_sirven_por_http_local(self) -> None:
        manejador = partial(_ManejadorSilencioso, directory=str(RAIZ / "web"))
        with ThreadingHTTPServer(("127.0.0.1", 0), manejador) as servidor:
            hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
            hilo.start()
            try:
                puerto = servidor.server_address[1]
                with urlopen(f"http://127.0.0.1:{puerto}/", timeout=5) as respuesta:
                    pagina = respuesta.read().decode("utf-8")
                    self.assertEqual(respuesta.status, 200)
                with urlopen(f"http://127.0.0.1:{puerto}/data/dashboard.json", timeout=5) as respuesta:
                    datos = json.loads(respuesta.read().decode("utf-8"))
                    self.assertEqual(respuesta.status, 200)
                with urlopen(f"http://127.0.0.1:{puerto}/data/intervenciones.json", timeout=5) as respuesta:
                    intervenciones = json.loads(respuesta.read().decode("utf-8"))
                    self.assertEqual(respuesta.status, 200)
                for recurso in ("css/styles.css", "js/app.js", "js/datos.js", "js/mapa.js", "js/intervenciones.js"):
                    with urlopen(f"http://127.0.0.1:{puerto}/{recurso}", timeout=5) as respuesta:
                        self.assertEqual(respuesta.status, 200, recurso)
                        self.assertGreater(len(respuesta.read()), 0, recurso)
                self.assertIn('href="css/styles.css"', pagina)
                self.assertIn('type="module" src="js/app.js"', pagina)
                self.assertNotIn("<style>", pagina)
                self.assertNotIn("<script>", pagina)
                self.assertIn('id="anio"', pagina)
                self.assertIn('id="barrio"', pagina)
                self.assertIn('id="categoria"', pagina)
                self.assertIn('id="map-zoom-in"', pagina)
                self.assertIn('id="layer-limite"', pagina)
                self.assertIn('id="layer-zonas"', pagina)
                self.assertEqual(datos["metadatos"]["registros"], 8332)
                self.assertEqual(intervenciones["metadatos"]["zonas_exploratorias"], 12)
                self.assertEqual(len(intervenciones["catalogo_intervenciones"]), 8)
                self.assertTrue(all(
                    zona["estado_evaluacion"] == "Pendiente de inspección"
                    for zona in intervenciones["zonas"]
                ))
            finally:
                servidor.shutdown()
                hilo.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
