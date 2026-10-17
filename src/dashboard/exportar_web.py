"""Exporta una vista web local derivada sin modificar los datos validados."""

from __future__ import annotations

import json
from pathlib import Path

from src.dashboard.datos import cargar_geojson, cargar_hechos, cargar_limite_manrique, validar_cierre
from src.dashboard.intervenciones import exportar_intervenciones


RAIZ = Path(__file__).resolve().parents[2]
RUTA_SALIDA = RAIZ / "web" / "data" / "dashboard.json"


def main() -> None:
    datos = cargar_hechos()
    validar_cierre(datos)
    columnas = [
        "evento_id", "anio", "barrio", "clase_siniestro", "gravedad_siniestro",
        "categoria_analisis", "zona_id", "distancia_carrera45_m", "latitud", "longitud",
    ]
    payload = {
        "metadatos": {"registros": len(datos), "periodo": "2019-2025", "version": "cierre_v1"},
        "eventos": datos[columnas].where(datos[columnas].notna(), None).to_dict(orient="records"),
        "limite_manrique": cargar_limite_manrique(),
        "carrera45": cargar_geojson("carrera45.geojson"),
        "zonas_prioritarias": cargar_geojson("zonas_prioritarias.geojson"),
    }
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_SALIDA.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    ruta_intervenciones = exportar_intervenciones()
    print(f"Dashboard exportado: {RUTA_SALIDA} ({len(datos)} eventos)")
    print(f"Módulo de intervenciones exportado: {ruta_intervenciones}")


if __name__ == "__main__":
    main()
