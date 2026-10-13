"""Analiza, de forma exploratoria, la distancia de siniestros al eje Carrera 45."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_EJE = RAIZ_PROYECTO / "data" / "processed" / "carrera45_manrique.geojson"
RUTA_SINIESTROS = RAIZ_PROYECTO / "data" / "processed" / "siniestros_comuna3_limpios.csv"
RUTA_COMUNAS = RAIZ_PROYECTO / "data" / "raw" / "comunas_medellin.geojson"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "analisis_distancias_siniestros_carrera45.txt"
RUTA_GRAFICO = RAIZ_PROYECTO / "reports" / "distribucion_distancias_siniestros_carrera45.png"
RUTA_MAPA = RAIZ_PROYECTO / "reports" / "mapa_siniestros_distancia_carrera45.png"
CRS_GEOGRAFICO = "EPSG:4326"
CRS_METRICO = "EPSG:9377"
UMBRALES = [10, 20, 30, 50, 75, 100, 150, 200]
UMBRALES_ANALISIS = [30, 50, 75, 100]


def cargar_eje() -> gpd.GeoDataFrame:
    """Carga y verifica el eje definitivo, cuya unidad lineal es metros."""
    eje = gpd.read_file(RUTA_EJE)
    if eje.crs is None or eje.crs.to_epsg() != 9377:
        raise ValueError(f"El eje debe estar en EPSG:9377; CRS encontrado: {eje.crs}")
    if eje.empty:
        raise ValueError("El eje definitivo no contiene segmentos.")
    return eje


def construir_siniestros() -> tuple[pd.DataFrame, gpd.GeoDataFrame, dict[str, int]]:
    """Crea puntos solo en memoria, conservando todas las filas del CSV original."""
    siniestros = pd.read_csv(RUTA_SINIESTROS)
    requeridas = {"latitud", "longitud", "clase_siniestro", "gravedad_siniestro", "anio"}
    faltantes = requeridas - set(siniestros.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el CSV: {sorted(faltantes)}")

    latitud = pd.to_numeric(siniestros["latitud"], errors="coerce")
    longitud = pd.to_numeric(siniestros["longitud"], errors="coerce")
    nulas = latitud.isna() | longitud.isna()
    invalidas = (~nulas) & (~latitud.between(-90, 90) | ~longitud.between(-180, 180))
    coordenadas_validas = ~(nulas | invalidas)

    # Se crea geometría únicamente para coordenadas válidas; las otras filas se conservan.
    geometria = gpd.points_from_xy(longitud.where(coordenadas_validas), latitud.where(coordenadas_validas))
    puntos = gpd.GeoDataFrame(siniestros.copy(), geometry=geometria, crs=CRS_GEOGRAFICO)
    puntos_metricos = puntos.to_crs(CRS_METRICO)

    validacion = {
        "registros": len(siniestros),
        "coordenadas_nulas": int(nulas.sum()),
        "coordenadas_invalidas": int(invalidas.sum()),
        "geometrias_nulas": int(puntos_metricos.geometry.isna().sum()),
        "geometrias_vacias": int(puntos_metricos.geometry.notna().sum() and puntos_metricos.geometry.dropna().is_empty.sum()),
    }
    return siniestros, puntos_metricos, validacion


def calcular_distancias(puntos: gpd.GeoDataFrame, eje: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Calcula la distancia mínima de cada punto válido al conjunto de segmentos."""
    resultado = puntos.copy()
    resultado["distancia_carrera45_m"] = pd.NA
    puntos_validos = resultado.geometry.notna() & ~resultado.geometry.is_empty
    eje_unificado = eje.geometry.union_all()
    resultado.loc[puntos_validos, "distancia_carrera45_m"] = resultado.loc[puntos_validos].geometry.distance(eje_unificado)
    resultado["distancia_carrera45_m"] = pd.to_numeric(resultado["distancia_carrera45_m"], errors="coerce")
    return resultado


def tabla_umbrales(distancias: pd.Series, total: int) -> pd.DataFrame:
    """Construye conteos acumulados respecto al total completo de siniestros."""
    filas = []
    for umbral in UMBRALES:
        cantidad = int((distancias <= umbral).sum())
        filas.append({"distancia": f"<= {umbral} m", "cantidad": cantidad, "porcentaje": cantidad / total * 100})
    return pd.DataFrame(filas)


def estadisticas(distancias: pd.Series) -> pd.Series:
    """Resume las distancias disponibles sin imponer ningún umbral de corredor."""
    validas = distancias.dropna()
    return pd.Series(
        {
            "mínima": validas.min(),
            "percentil 25": validas.quantile(0.25),
            "mediana": validas.median(),
            "percentil 75": validas.quantile(0.75),
            "percentil 90": validas.quantile(0.90),
            "máxima": validas.max(),
        }
    )


def analisis_por_atributo(datos: gpd.GeoDataFrame, atributo: str) -> dict[int, pd.DataFrame]:
    """Cuenta siniestros cercanos por categoría para cada umbral exploratorio."""
    resultado: dict[int, pd.DataFrame] = {}
    for umbral in UMBRALES_ANALISIS:
        cercanos = datos.loc[datos["distancia_carrera45_m"] <= umbral]
        tabla = cercanos.groupby(atributo, dropna=False).size().reset_index(name="cantidad")
        tabla["porcentaje_del_umbral"] = tabla["cantidad"] / len(cercanos) * 100 if len(cercanos) else 0.0
        resultado[umbral] = tabla.sort_values("cantidad", ascending=False)
    return resultado


def agregar_tabla(lineas: list[str], tabla: pd.DataFrame, decimales: int = 2) -> None:
    """Añade una tabla legible al reporte de texto."""
    if tabla.empty:
        lineas.append("Sin registros.")
    else:
        lineas.append(tabla.to_string(index=False, float_format=lambda valor: f"{valor:.{decimales}f}"))


def crear_reporte(
    validacion: dict[str, int], umbrales: pd.DataFrame, resumen: pd.Series, datos: gpd.GeoDataFrame
) -> None:
    """Guarda resultados completos y deja explícito el carácter exploratorio."""
    lineas = [
        "ANÁLISIS EXPLORATORIO DE DISTANCIAS — SINIESTROS Y CARRERA 45",
        "",
        "Esta etapa no define el ancho definitivo del corredor ni descarta siniestros.",
        "Las distancias se calcularon en metros con EPSG:9377, desde cada Point válido al eje definitivo.",
        "",
        "VALIDACIÓN DE INSUMOS",
        f"Siniestros cargados: {validacion['registros']}",
        f"Coordenadas nulas: {validacion['coordenadas_nulas']}",
        f"Coordenadas inválidas: {validacion['coordenadas_invalidas']}",
        f"Geometrías nulas: {validacion['geometrias_nulas']}",
        f"Geometrías vacías: {validacion['geometrias_vacias']}",
        f"CRS final de puntos: {CRS_METRICO}",
        "",
        "DISTRIBUCIÓN ACUMULADA DE DISTANCIAS",
    ]
    agregar_tabla(lineas, umbrales)
    lineas.extend(["", "ESTADÍSTICAS DE DISTANCIA (m)"])
    agregar_tabla(lineas, resumen.rename_axis("estadística").reset_index(name="metros"))

    for atributo in ["clase_siniestro", "gravedad_siniestro", "anio"]:
        lineas.extend(["", f"ANÁLISIS POR {atributo.upper()}"])
        for umbral, tabla in analisis_por_atributo(datos, atributo).items():
            lineas.append(f"\nDistancia <= {umbral} m")
            agregar_tabla(lineas, tabla)

    RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
    RUTA_REPORTE.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def crear_grafico(distancias: pd.Series) -> None:
    """Muestra el tramo cercano (hasta p99) para que los valores lejanos no dominen el gráfico."""
    validas = distancias.dropna()
    limite = max(100.0, float(validas.quantile(0.99)))
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    ax.hist(validas[validas <= limite], bins=50, color="#0077b6", edgecolor="white")
    for umbral in [30, 50, 75, 100]:
        ax.axvline(umbral, color="#e63946", linestyle="--", linewidth=1)
        ax.text(umbral, ax.get_ylim()[1] * 0.92, f"{umbral} m", rotation=90, color="#a4161a", va="top", ha="right")
    ax.set_title("Distribución de distancias cercanas al eje de Carrera 45")
    ax.set_xlabel("Distancia mínima al eje (m)")
    ax.set_ylabel("Cantidad de siniestros")
    ax.set_xlim(0, limite)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(RUTA_GRAFICO, dpi=250, bbox_inches="tight")
    plt.close(fig)


def cargar_manrique() -> gpd.GeoDataFrame:
    """Carga exclusivamente el límite oficial de la Comuna 3 para contexto cartográfico."""
    comunas = gpd.read_file(RUTA_COMUNAS)
    manrique = comunas.loc[(comunas["codigo"].astype(str).str.zfill(2) == "03") & (comunas["nombre"].str.casefold() == "manrique")].copy()
    if manrique.empty:
        raise ValueError("No se encontró el polígono oficial de Comuna 3 - Manrique.")
    return manrique.to_crs(CRS_METRICO)


def crear_mapa(datos: gpd.GeoDataFrame, eje: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame) -> None:
    """Mapa legible de siniestros hasta 100 m; no representa los puntos más lejanos."""
    rangos = [
        (0, 30, "0–30 m", "#d62828"),
        (30, 50, "30–50 m", "#f77f00"),
        (50, 75, "50–75 m", "#fcbf49"),
        (75, 100, "75–100 m", "#457b9d"),
    ]
    fig, ax = plt.subplots(figsize=(9, 10), constrained_layout=True)
    manrique.plot(ax=ax, facecolor="#edf6f9", edgecolor="#1d3557", linewidth=1.2)
    for inferior, superior, etiqueta, color in rangos:
        seleccion = datos.loc[(datos["distancia_carrera45_m"] > inferior) & (datos["distancia_carrera45_m"] <= superior)]
        if inferior == 0:
            seleccion = datos.loc[(datos["distancia_carrera45_m"] >= inferior) & (datos["distancia_carrera45_m"] <= superior)]
        seleccion.plot(ax=ax, color=color, markersize=8, alpha=0.75)
    eje.plot(ax=ax, color="#003049", linewidth=2.2)
    handles = [Patch(facecolor="#edf6f9", edgecolor="#1d3557", label="Límite oficial de Manrique")]
    handles += [Line2D([0], [0], marker="o", linestyle="", color=color, markersize=6, label=etiqueta) for _, _, etiqueta, color in rangos]
    handles += [Line2D([0], [0], color="#003049", linewidth=2.2, label="Eje definitivo Carrera 45")]
    ax.legend(handles=handles, loc="best", title="Elementos")
    ax.set_title("Siniestros cercanos al eje definitivo de Carrera 45")
    ax.set_xlabel("Coordenada X (m) — EPSG:9377")
    ax.set_ylabel("Coordenada Y (m) — EPSG:9377")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.savefig(RUTA_MAPA, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Ejecuta el perfil exploratorio de distancias y publica sus tres productos."""
    if not RUTA_EJE.exists() or not RUTA_SINIESTROS.exists() or not RUTA_COMUNAS.exists():
        raise FileNotFoundError("Falta el eje definitivo, el CSV de siniestros o la capa de comunas.")
    eje = cargar_eje()
    _, puntos, validacion = construir_siniestros()
    resultados = calcular_distancias(puntos, eje)
    umbrales = tabla_umbrales(resultados["distancia_carrera45_m"], len(resultados))
    resumen = estadisticas(resultados["distancia_carrera45_m"])
    crear_reporte(validacion, umbrales, resumen, resultados)
    crear_grafico(resultados["distancia_carrera45_m"])
    crear_mapa(resultados, eje, cargar_manrique())

    print("ANÁLISIS EXPLORATORIO DE DISTANCIAS")
    print(f"Siniestros: {validacion['registros']}")
    print(f"CRS final: {CRS_METRICO}")
    print(umbrales.to_string(index=False, float_format=lambda valor: f"{valor:.2f}"))
    print("\nEstadísticas (m):")
    print(resumen.to_string(float_format=lambda valor: f"{valor:.2f}"))
    print(f"\nReporte: {RUTA_REPORTE}")
    print(f"Gráfico: {RUTA_GRAFICO}")
    print(f"Mapa: {RUTA_MAPA}")


if __name__ == "__main__":
    main()
