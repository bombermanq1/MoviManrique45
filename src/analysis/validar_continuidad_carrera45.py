"""Valida la continuidad del eje preliminar de Carrera 45 en Manrique."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_PRELIMINAR = RAIZ_PROYECTO / "data" / "processed" / "carrera45_manrique_preliminar.geojson"
RUTA_COMUNAS = RAIZ_PROYECTO / "data" / "raw" / "comunas_medellin.geojson"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "validacion_final_continuidad_carrera45.txt"
RUTA_MAPA = RAIZ_PROYECTO / "reports" / "mapa_validacion_final_carrera45.png"
CRS_METRICO = "EPSG:9377"
OID_REVISION = 13704


class Reporte:
    """Escribe el mismo diagnóstico en consola y en un archivo de texto."""

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def agregar(self, texto: Any = "") -> None:
        contenido = str(texto)
        print(contenido)
        self.lineas.append(contenido)

    def guardar(self) -> None:
        RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
        RUTA_REPORTE.write_text("\n".join(self.lineas) + "\n", encoding="utf-8")


def extremos(geometria) -> list[Point]:
    """Extrae extremos de LineString y MultiLineString sin alterar geometrías."""
    if geometria.geom_type == "LineString":
        coordenadas = list(geometria.coords)
        return [Point(coordenadas[0]), Point(coordenadas[-1])]
    if geometria.geom_type == "MultiLineString":
        return [punto for linea in geometria.geoms for punto in extremos(linea)]
    return []


def es_transversal(geometria) -> bool:
    """Detecta tramos con extensión este-oeste mayor que norte-sur."""
    xmin, ymin, xmax, ymax = geometria.bounds
    return (xmax - xmin) > (ymax - ymin)


def cargar_fuentes() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Carga el eje preliminar y el límite oficial ya en CRS métrico."""
    if not RUTA_PRELIMINAR.exists() or not RUTA_COMUNAS.exists():
        raise FileNotFoundError("Falta el eje preliminar o la capa territorial de comunas.")
    eje = gpd.read_file(RUTA_PRELIMINAR).to_crs(CRS_METRICO).reset_index(drop=True)
    comunas = gpd.read_file(RUTA_COMUNAS).to_crs(CRS_METRICO)
    manrique = comunas.loc[
        comunas["codigo"].fillna("").astype(str).str.strip().eq("03")
        & comunas["nombre"].fillna("").astype(str).str.strip().str.casefold().eq("manrique")
    ].copy()
    if len(manrique) != 1:
        raise ValueError("No se encontró un único polígono oficial de Manrique.")
    return eje, manrique


def componentes_exactos(eje: gpd.GeoDataFrame) -> list[set[int]]:
    """Construye componentes mediante contacto geométrico exacto entre segmentos."""
    geometrias = eje.geometry.tolist()
    adyacencias = [
        [j for j, otra in enumerate(geometrias) if geometria.intersects(otra)]
        for geometria in geometrias
    ]
    pendientes = set(range(len(eje)))
    componentes: list[set[int]] = []
    while pendientes:
        pila = [pendientes.pop()]
        componente = set(pila)
        while pila:
            indice = pila.pop()
            vecinos = set(adyacencias[indice]) & pendientes
            pendientes -= vecinos
            pila.extend(vecinos)
            componente |= vecinos
        componentes.append(componente)
    return componentes


def ordenar_componentes(componentes: list[set[int]], eje: gpd.GeoDataFrame) -> list[set[int]]:
    """Ordena componentes de sur a norte con el límite sur de sus geometrías."""
    return sorted(
        componentes,
        key=lambda componente: eje.iloc[sorted(componente)].geometry.union_all().bounds[1],
    )


def distancia_extremos(componentes_a: set[int], componentes_b: set[int], eje: gpd.GeoDataFrame) -> float:
    """Mide el menor gap entre extremos de dos componentes en metros."""
    extremos_a = [
        punto for indice in componentes_a for punto in extremos(eje.geometry.iloc[indice])
    ]
    extremos_b = [
        punto for indice in componentes_b for punto in extremos(eje.geometry.iloc[indice])
    ]
    return min(punto_a.distance(punto_b) for punto_a in extremos_a for punto_b in extremos_b)


def describir_componentes(
    componentes: list[set[int]], eje: gpd.GeoDataFrame, reporte: Reporte
) -> None:
    """Lista miembros, longitud y condición de aislamiento de cada componente exacto."""
    reporte.agregar("\n=== COMPONENTES CONECTADOS POR CONTACTO EXACTO ===")
    for numero, componente in enumerate(componentes, start=1):
        filas = eje.iloc[sorted(componente)]
        objectids = [int(valor) for valor in filas["objectid"].tolist()]
        reporte.agregar(
            f"Componente {numero}: objectid={objectids}; segmentos={len(filas)}; "
            f"longitud={filas.geometry.length.sum():.2f} m"
        )


def generar_reporte(
    eje: gpd.GeoDataFrame,
    componentes: list[set[int]],
    eje_principal: gpd.GeoDataFrame,
    excluidos: gpd.GeoDataFrame,
    reporte: Reporte,
) -> None:
    """Documenta continuidad, gaps y la propuesta técnica sobre el segmento 13704."""
    reporte.agregar("VALIDACIÓN FINAL DE CONTINUIDAD — CARRERA 45, MANRIQUE")
    reporte.agregar(f"Segmentos analizados: {len(eje)}")
    reporte.agregar(f"CRS de análisis: {eje.crs}")
    describir_componentes(componentes, eje, reporte)

    aislados = [
        int(eje.iloc[next(iter(componente))]["objectid"])
        for componente in componentes if len(componente) == 1
    ]
    reporte.agregar(f"\nSegmentos aislados por contacto exacto: {aislados}")

    # El eje principal se compone de todos los tramos longitudinales; los componentes
    # se ordenan sur-norte para reportar los gaps entre extremos consecutivos.
    componentes_principales = ordenar_componentes(
        [
            componente for componente in componentes
            if not any(int(eje.iloc[indice]["objectid"]) == OID_REVISION for indice in componente)
        ],
        eje,
    )
    reporte.agregar("\n=== GAPS ENTRE COMPONENTES LONGITUDINALES CONSECUTIVOS ===")
    for i, (actual, siguiente) in enumerate(zip(componentes_principales, componentes_principales[1:]), start=1):
        ids_actual = [int(valor) for valor in eje.iloc[sorted(actual)]["objectid"].tolist()]
        ids_siguiente = [int(valor) for valor in eje.iloc[sorted(siguiente)]["objectid"].tolist()]
        gap = distancia_extremos(actual, siguiente, eje)
        reporte.agregar(
            f"C{i} {ids_actual} -> C{i + 1} {ids_siguiente}: gap mínimo entre extremos = {gap:.2f} m"
        )

    transversales = eje.loc[eje.geometry.map(es_transversal)]
    reporte.agregar(f"\nSegmentos con comportamiento transversal: {transversales['objectid'].astype(int).tolist()}")
    reporte.agregar(f"Objectids del eje longitudinal principal: {eje_principal['objectid'].astype(int).tolist()}")
    reporte.agregar(f"Longitud total del eje principal: {eje_principal.geometry.length.sum():.2f} m")
    reporte.agregar(f"Segmentos excluidos/revisión: {excluidos['objectid'].astype(int).tolist()}")
    reporte.agregar(
        "Decisión técnica sobre 13704: EXCLUIR del eje definitivo propuesto. "
        "Está dentro de Manrique, pero es el único tramo con orientación predominantemente "
        "este-oeste y funciona como ramificación transversal, no como continuación longitudinal."
    )
    otros_revision = [int(valor) for valor in transversales["objectid"].tolist() if int(valor) != OID_REVISION]
    reporte.agregar(f"Otros segmentos que requieren revisión por comportamiento similar: {otros_revision}")
    reporte.agregar("No se creó ningún GeoJSON definitivo en esta etapa.")


def crear_mapa(manrique: gpd.GeoDataFrame, eje_principal: gpd.GeoDataFrame, excluidos: gpd.GeoDataFrame) -> None:
    """Representa únicamente Manrique, el eje longitudinal y segmentos de revisión."""
    fig, ax = plt.subplots(figsize=(9, 10), constrained_layout=True)
    manrique.plot(ax=ax, facecolor="#edf6f9", edgecolor="#1d3557", linewidth=1.4)
    eje_principal.plot(ax=ax, color="#0077b6", linewidth=2.6, label="Eje longitudinal principal")
    excluidos.plot(ax=ax, color="#d62828", linewidth=3.5, label="Excluido / revisión")
    for _, fila in excluidos.iterrows():
        punto = fila.geometry.representative_point()
        ax.annotate(
            f"OID {int(fila['objectid'])}", (punto.x, punto.y), xytext=(6, 6),
            textcoords="offset points", fontsize=8,
            bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.85},
        )
    ax.set_title("Validación final de continuidad — Carrera 45, Manrique")
    ax.set_xlabel("Coordenada X (m) — EPSG:9377")
    ax.set_ylabel("Coordenada Y (m) — EPSG:9377")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend(loc="best")
    RUTA_MAPA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(RUTA_MAPA, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Ejecuta solo el diagnóstico de continuidad; no escribe el eje definitivo."""
    reporte = Reporte()
    try:
        eje, manrique = cargar_fuentes()
        componentes = ordenar_componentes(componentes_exactos(eje), eje)
        transversal = eje.geometry.map(es_transversal)
        excluidos = eje.loc[eje["objectid"].eq(OID_REVISION) | transversal].copy()
        eje_principal = eje.loc[~eje.index.isin(excluidos.index)].copy()
        generar_reporte(eje, componentes, eje_principal, excluidos, reporte)
        crear_mapa(manrique, eje_principal, excluidos)
        reporte.agregar(f"\nMapa de validación guardado en: {RUTA_MAPA}")
    except (FileNotFoundError, ValueError, OSError) as error:
        reporte.agregar(f"No se pudo completar la validación: {error}")
    finally:
        reporte.guardar()
        print(f"Reporte guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()
