"""Controles estáticos: ningún módulo PostgreSQL debe actuar al importarse."""

from __future__ import annotations

from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[1]


class SeguridadPostgresTests(unittest.TestCase):
    def test_carga_exige_bandera_explicita_para_escritura(self) -> None:
        contenido = (RAIZ / "src" / "etl" / "cargar_carrera45_postgis.py").read_text(encoding="utf-8")
        self.assertIn('"--permitir-escritura"', contenido)
        self.assertIn("if not argumentos.permitir_escritura", contenido)
        self.assertIn('if __name__ == "__main__":', contenido)

    def test_prueba_de_conexion_no_se_ejecuta_al_importar(self) -> None:
        contenido = (RAIZ / "src" / "etl" / "probar_conexion_postgres.py").read_text(encoding="utf-8")
        self.assertIn('if __name__ == "__main__":', contenido)


if __name__ == "__main__":
    unittest.main()
