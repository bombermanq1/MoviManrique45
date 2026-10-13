
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_MALLA = RAIZ_PROYECTO / "data" / "raw" / "malla_vial_medellin.geojson"
RUTA_SALIDA = RAIZ_PROYECTO / "reports" / "mapa_diagnostico_carrera45.png"

OIDS_CR45_COMUNA04 = [24568, 23780, 25862, 26016, 21844]
OIDS_CR45A = [34900, 12651]
OID_TRANSVERSAL = 13704
OID_REFERENCIA_CL93 = 710


def es_vacio(serie):

    return serie.isna() | serie.astype(str).str.strip().eq("")


def cargar_y_proyectar(ruta: Path) -> gpd.GeoDataFrame:

    malla = gpd.read_file(ruta)

    # Las coordenadas almacenadas son geográficas (-75, 6), aunque el archivo
    # declare EPSG:9377. No se reescribe el RAW: se reasigna y proyecta en memoria.
    return malla.set_crs("EPSG:4326", allow_override=True).to_crs(epsg=9377)


def seleccionar_capas(malla: gpd.GeoDataFrame) -> dict[str, gpd.GeoDataFrame]:
    """Construye las capas visuales sin unir, modificar ni guardar geometrías."""
    candidatos = malla.loc[
        malla["tipo_via"].eq("CR")
        & malla["numero_via"].eq(45)
        & malla["comuna"].eq("03")
        & es_vacio(malla["apendice_via"])
        & es_vacio(malla["orientacion_via"])
    ].copy()

    capas = {
        "candidatos": candidatos,
        "cr45_comuna04": malla.loc[malla["objectid"].isin(OIDS_CR45_COMUNA04)].copy(),
        "cr45a": malla.loc[malla["objectid"].isin(OIDS_CR45A)].copy(),
        "transversal": malla.loc[malla["objectid"].eq(OID_TRANSVERSAL)].copy(),
        "cl93": malla.loc[malla["objectid"].eq(OID_REFERENCIA_CL93)].copy(),
    }

    faltantes = {
        nombre: capa.empty for nombre, capa in capas.items() if nombre != "candidatos"
    }
    if len(candidatos) != 22 or any(faltantes.values()):
        raise ValueError(
            "No se localizaron todos los segmentos esperados para el mapa: "
            f"candidatos={len(candidatos)}, faltantes={faltantes}"
        )
    return capas


def agregar_norte_y_escala(ax, xmin: float, ymin: float, xmax: float, ymax: float) -> None:
    """Añade orientación norte y una escala métrica aproximada al área visible."""
    ancho = xmax - xmin
    alto = ymax - ymin
    x_norte = xmax - ancho * 0.06
    y_base = ymax - alto * 0.18
    largo_flecha = alto * 0.10
    ax.annotate(
        "N",
        xy=(x_norte, y_base + largo_flecha),
        xytext=(x_norte, y_base),
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "black", "lw": 1.5},
    )

    escala_metros = 250
    x_escala = xmin + ancho * 0.06
    y_escala = ymin + alto * 0.07
    ax.plot([x_escala, x_escala + escala_metros], [y_escala, y_escala], color="black", lw=2)
    ax.plot([x_escala, x_escala], [y_escala - 8, y_escala + 8], color="black", lw=1)
    ax.plot(
        [x_escala + escala_metros, x_escala + escala_metros],
        [y_escala - 8, y_escala + 8],
        color="black",
        lw=1,
    )
    ax.text(
        x_escala + escala_metros / 2,
        y_escala + alto * 0.025,
        "250 m",
        ha="center",
        va="bottom",
        fontsize=8,
    )


def etiquetar_segmentos(ax, capas: dict[str, gpd.GeoDataFrame]) -> None:
    """Coloca etiquetas pequeñas para los segmentos que requieren revisión visual."""
    desplazamientos = {
        24568: (4, 4),
        23780: (4, 4),
        25862: (4, 4),
        26016: (4, 4),
        21844: (4, 4),
        34900: (4, 10),
        12651: (-38, -8),
        13704: (14, 6),
        710: (-18, 10),
    }
    relevantes = [
        capas["cr45_comuna04"],
        capas["cr45a"],
        capas["transversal"],
        capas["cl93"],
    ]
    for capa in relevantes:
        for _, fila in capa.iterrows():
            punto = fila.geometry.representative_point()
            objectid = int(fila["objectid"])
            ax.annotate(
                str(objectid),
                xy=(punto.x, punto.y),
                xytext=desplazamientos.get(objectid, (4, 4)),
                textcoords="offset points",
                fontsize=7,
                color="black",
                bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.75},
            )


def crear_mapa(malla: gpd.GeoDataFrame, capas: dict[str, gpd.GeoDataFrame]) -> None:
    """Dibuja el contexto vial y las categorías de diagnóstico solicitadas."""
    fig, ax = plt.subplots(figsize=(11, 12), constrained_layout=True)

    # Contexto de la malla cercano al corredor; no se altera ninguna geometría.
    malla.plot(ax=ax, color="#d9d9d9", linewidth=0.25, alpha=0.65, zorder=1)
    capas["candidatos"].plot(ax=ax, color="#006d77", linewidth=2.2, zorder=3)
    capas["cr45_comuna04"].plot(ax=ax, color="#f28e2b", linewidth=3.0, zorder=4)
    capas["cr45a"].plot(ax=ax, color="#7b2cbf", linewidth=3.2, zorder=5)
    capas["transversal"].plot(ax=ax, color="#d62828", linewidth=3.6, zorder=6)
    capas["cl93"].plot(ax=ax, color="#202020", linewidth=3.0, linestyle="--", zorder=6)

    # El encuadre se deriva de segmentos relevantes y conserva contexto vial local.
    relevantes = gpd.GeoSeries(
        pd_concat_geometries(capas), crs=malla.crs
    )
    xmin, ymin, xmax, ymax = relevantes.total_bounds
    margen = 300
    ax.set_xlim(xmin - margen, xmax + margen)
    ax.set_ylim(ymin - margen, ymax + margen)

    etiquetar_segmentos(ax, capas)
    agregar_norte_y_escala(ax, xmin - margen, ymin - margen, xmax + margen, ymax + margen)

    leyenda = [
        Line2D([0], [0], color="#006d77", lw=2.5, label="22 candidatos originales (Comuna 03)"),
        Line2D([0], [0], color="#f28e2b", lw=3, label="CR 45 en Comuna 04"),
        Line2D([0], [0], color="#7b2cbf", lw=3, label="CR 45A"),
        Line2D([0], [0], color="#d62828", lw=3.5, label="13704: tramo transversal"),
        Line2D([0], [0], color="#202020", lw=3, linestyle="--", label="710: CL 93 (referencia)"),
    ]
    ax.legend(handles=leyenda, loc="lower left", frameon=True, fontsize=8)
    ax.set_title("Diagnóstico de continuidad: Carrera 45 — Comuna 3, Manrique", fontsize=14, fontweight="bold")
    ax.set_xlabel("Coordenada X (m) — EPSG:9377")
    ax.set_ylabel("Coordenada Y (m) — EPSG:9377")
    ax.grid(True, linewidth=0.35, alpha=0.45)
    ax.set_aspect("equal")

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(RUTA_SALIDA, dpi=300, bbox_inches="tight")
    plt.close(fig)


def pd_concat_geometries(capas: dict[str, gpd.GeoDataFrame]):
    """Devuelve geometrías relevantes sin depender de una operación de unión espacial."""
    geometries = []
    for capa in capas.values():
        geometries.extend(capa.geometry.tolist())
    return geometries


def main() -> None:
    """Carga, clasifica visualmente y exporta la imagen de diagnóstico."""
    if not RUTA_MALLA.exists():
        raise FileNotFoundError(f"No se encontró la fuente RAW: {RUTA_MALLA}")

    malla = cargar_y_proyectar(RUTA_MALLA)
    capas = seleccionar_capas(malla)
    crear_mapa(malla, capas)
    print(f"Mapa de diagnóstico guardado en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
