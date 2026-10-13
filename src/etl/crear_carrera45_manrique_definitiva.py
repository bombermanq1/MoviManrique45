"""Publica el eje definitivo de Carrera 45 dentro de Comuna 3 - Manrique."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_PRELIMINAR = RAIZ_PROYECTO / "data" / "processed" / "carrera45_manrique_preliminar.geojson"
RUTA_COMUNAS = RAIZ_PROYECTO / "data" / "raw" / "comunas_medellin.geojson"
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "processed" / "carrera45_manrique.geojson"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "reporte_carrera45_manrique_definitiva.txt"
RUTA_MAPA = RAIZ_PROYECTO / "reports" / "mapa_carrera45_manrique_definitiva.png"
CRS_METRICO = "EPSG:9377"
OID_EXCLUIDO = 13704
LONGITUD_ESPERADA_M = 1698.67
TOLERANCIA_LONGITUD_M = 0.1
TOLERANCIA_TERRITORIAL_M = 1e-3


class Reporte:
    """Mantiene el mismo contenido en consola y en el reporte de trazabilidad."""

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def agregar(self, texto: Any = "") -> None:
        contenido = str(texto)
        print(contenido)
        self.lineas.append(contenido)

    def guardar(self) -> None:
        RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
        RUTA_REPORTE.write_text("\n".join(self.lineas) + "\n", encoding="utf-8")


def cargar_manrique() -> gpd.GeoDataFrame:
    """Carga exclusivamente el polígono oficial de Comuna 3 - Manrique."""
    comunas = gpd.read_file(RUTA_COMUNAS).to_crs(CRS_METRICO)
    manrique = comunas.loc[
        comunas["codigo"].fillna("").astype(str).str.strip().eq("03")
        & comunas["nombre"].fillna("").astype(str).str.strip().str.casefold().eq("manrique")
    ].copy()
    if len(manrique) != 1:
        raise ValueError("No se encontró un único polígono oficial de Comuna 3 - Manrique.")
    return manrique


def cargar_eje_preliminar() -> gpd.GeoDataFrame:
    """Carga el eje previamente recortado y excluye solo la ramificación transversal."""
    eje = gpd.read_file(RUTA_PRELIMINAR).to_crs(CRS_METRICO)
    if "objectid" not in eje.columns:
        raise ValueError("El eje preliminar no contiene objectid para mantener trazabilidad.")
    if not eje["objectid"].eq(OID_EXCLUIDO).any():
        raise ValueError("El eje preliminar no contiene objectid 13704 para aplicar la decisión validada.")
    return eje.loc[~eje["objectid"].eq(OID_EXCLUIDO)].copy()


def validar_eje(eje: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame) -> dict[str, Any]:
    """Verifica integridad geométrica, territorio, cantidad y longitud definitiva."""
    poligono = manrique.geometry.union_all()
    longitud_fuera = eje.geometry.difference(poligono).length
    validacion = {
        "crs": str(eje.crs),
        "segmentos": len(eje),
        "longitud_total_m": float(eje.geometry.length.sum()),
        "geometrias_nulas": int(eje.geometry.isna().sum()),
        "geometrias_vacias": int(eje.geometry.is_empty.sum()),
        "geometrias_invalidas": int((~eje.geometry.is_valid).sum()),
        "geometrias_fuera_manrique": int(longitud_fuera.gt(TOLERANCIA_TERRITORIAL_M).sum()),
        "contiene_13704": bool(eje["objectid"].eq(OID_EXCLUIDO).any()),
    }
    if validacion["crs"] != CRS_METRICO:
        raise ValueError(f"CRS inesperado: {validacion['crs']}")
    if validacion["segmentos"] != 26:
        raise ValueError(f"Cantidad inesperada de segmentos: {validacion['segmentos']}")
    if abs(validacion["longitud_total_m"] - LONGITUD_ESPERADA_M) > TOLERANCIA_LONGITUD_M:
        raise ValueError(f"Longitud inesperada: {validacion['longitud_total_m']:.2f} m")
    if any(validacion[clave] for clave in (
        "geometrias_nulas", "geometrias_vacias", "geometrias_invalidas",
        "geometrias_fuera_manrique", "contiene_13704",
    )):
        raise ValueError(f"Validación geométrica fallida: {validacion}")
    return validacion


def crear_reporte(eje: gpd.GeoDataFrame, validacion: dict[str, Any], reporte: Reporte) -> None:
    """Registra el criterio territorial y la decisión definitiva de selección."""
    objectids = [int(valor) for valor in eje["objectid"].tolist()]
    reporte.agregar("REPORTE — EJE DEFINITIVO CARRERA 45, COMUNA 3 - MANRIQUE")
    reporte.agregar("Criterio territorial: se conserva exclusivamente la geometría ya recortada al polígono oficial de Comuna 3 - Manrique.")
    reporte.agregar("Criterio de selección: segmentos CR 45 del eje preliminar; se excluye solo la ramificación transversal validada.")
    reporte.agregar("Exclusión: objectid 13704; motivo: ramificación transversal, no continuación del eje longitudinal. No se excluyó por estar fuera de Manrique.")
    reporte.agregar(f"Número final de segmentos: {validacion['segmentos']}")
    reporte.agregar(f"Longitud total: {validacion['longitud_total_m']:.2f} m")
    reporte.agregar(f"CRS: {validacion['crs']}")
    reporte.agregar(f"Objectids incluidos: {objectids}")
    reporte.agregar("Gaps conocidos: 64.04 m, 7.73 m, 99.03 m, 100.91 m, 11.33 m, 8.54 m, 2.59 m y 137.31 m.")
    reporte.agregar("Los gaps se mantienen: no se rellenaron con líneas artificiales ni se extendió el eje fuera de Manrique.")
    reporte.agregar(f"Geometrías nulas: {validacion['geometrias_nulas']}")
    reporte.agregar(f"Geometrías vacías: {validacion['geometrias_vacias']}")
    reporte.agregar(f"Geometrías inválidas: {validacion['geometrias_invalidas']}")
    reporte.agregar(f"Geometrías fuera de Manrique: {validacion['geometrias_fuera_manrique']}")


def crear_mapa(manrique: gpd.GeoDataFrame, eje: gpd.GeoDataFrame) -> None:
    """Dibuja el límite oficial y el eje definitivo, sin mostrar la ramificación excluida."""
    fig, ax = plt.subplots(figsize=(9, 10), constrained_layout=True)
    manrique.plot(ax=ax, facecolor="#edf6f9", edgecolor="#1d3557", linewidth=1.4, label="Límite oficial de Manrique")
    eje.plot(ax=ax, color="#0077b6", linewidth=2.7, label="Eje definitivo Carrera 45")
    ax.set_title("Eje definitivo de Carrera 45 — Comuna 3, Manrique")
    ax.set_xlabel("Coordenada X (m) — EPSG:9377")
    ax.set_ylabel("Coordenada Y (m) — EPSG:9377")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    # Se usan elementos de leyenda explícitos porque GeoPandas dibuja el
    # polígono como una colección que Matplotlib no incorpora automáticamente.
    ax.legend(
        handles=[
            Patch(facecolor="#edf6f9", edgecolor="#1d3557", label="Límite oficial de Manrique"),
            Line2D([0], [0], color="#0077b6", linewidth=2.7, label="Eje definitivo Carrera 45"),
        ],
        loc="best",
    )
    RUTA_MAPA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(RUTA_MAPA, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Genera la capa definitiva sin crear geometrías nuevas ni reparar gaps."""
    reporte = Reporte()
    try:
        if not RUTA_PRELIMINAR.exists() or not RUTA_COMUNAS.exists():
            raise FileNotFoundError("Falta el eje preliminar o el límite oficial de Manrique.")
        manrique = cargar_manrique()
        eje = cargar_eje_preliminar()
        validacion = validar_eje(eje, manrique)
        RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
        eje.to_file(RUTA_SALIDA, driver="GeoJSON")
        crear_mapa(manrique, eje)
        crear_reporte(eje, validacion, reporte)
        reporte.agregar(f"\nGeoJSON definitivo guardado en: {RUTA_SALIDA}")
        reporte.agregar(f"Mapa definitivo guardado en: {RUTA_MAPA}")
    except (FileNotFoundError, ValueError, OSError) as error:
        reporte.agregar(f"No se generó el eje definitivo: {error}")
    finally:
        reporte.guardar()
        print(f"Reporte guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()
