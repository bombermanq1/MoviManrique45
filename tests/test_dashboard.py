"""Controles de integridad para el dashboard web."""

import unittest

from src.dashboard.datos import cargar_hechos, validar_cierre


class DashboardTests(unittest.TestCase):
    def test_dashboard_preserva_cierre(self) -> None:
        resultado = validar_cierre(cargar_hechos())
        self.assertEqual(resultado["filas"], 8332)
        self.assertEqual(resultado["principal_50m"], 604)
        self.assertEqual(resultado["sensibilidad_borde"], 40)
        self.assertEqual(resultado["revision_territorial"], 4)
        self.assertEqual(resultado["resto_manrique"], 7684)

    def test_union_fecha_coordenadas_es_univoca(self) -> None:
        datos = cargar_hechos()
        self.assertTrue(datos["evento_id"].is_unique)
        self.assertEqual(datos[["fecha_siniestro", "latitud", "longitud"]].isna().sum().sum(), 0)

    def test_dashboard_detecta_cambio_de_ids_de_borde(self) -> None:
        """Un intercambio que preserve conteos no puede alterar el cierre congelado."""
        datos = cargar_hechos()
        borde = datos.index[datos["categoria_analisis"].eq("sensibilidad_borde")][0]
        resto = datos.index[datos["categoria_analisis"].eq("resto_manrique")][0]
        alterados = datos.copy()
        alterados.loc[borde, "categoria_analisis"] = "resto_manrique"
        alterados.loc[resto, "categoria_analisis"] = "sensibilidad_borde"

        with self.assertRaisesRegex(ValueError, "sensibilidad_borde"):
            validar_cierre(alterados)
