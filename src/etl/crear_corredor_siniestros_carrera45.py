"""Crea el corredor analítico de 50 m de Carrera 45 y sus siniestros asociados."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
RUTA_EJE = RAIZ / "data" / "processed" / "carrera45_manrique.geojson"
RUTA_SINIESTROS = RAIZ / "data" / "processed" / "siniestros_comuna3_limpios.csv"
RUTA_COMUNAS = RAIZ / "data" / "raw" / "comunas_medellin.geojson"
RUTA_CORREDOR = RAIZ / "data" / "processed" / "corredor_carrera45_50m.geojson"
RUTA_SELECCIONADOS = RAIZ / "data" / "processed" / "siniestros_carrera45_50m.csv"
RUTA_REPORTE = RAIZ / "reports" / "reporte_corredor_carrera45_50m.txt"
RUTA_MAPA = RAIZ / "reports" / "mapa_corredor_siniestros_carrera45_50m.png"
CRS_GEOGRAFICO = "EPSG:4326"
CRS_METRICO = "EPSG:9377"
DISTANCIA_BUFFER_M = 50.0
TOLERANCIA_M = 1e-6


def cargar_eje() -> gpd.GeoDataFrame:
    """Carga el eje definitivo y comprueba su CRS métrico."""
    eje = gpd.read_file(RUTA_EJE)
    if eje.crs is None or eje.crs.to_epsg() != 9377:
        raise ValueError(f"El eje debe estar en EPSG:9377; CRS encontrado: {eje.crs}")
    if len(eje) != 26:
        raise ValueError(f"Se esperaban 26 segmentos del eje definitivo; se obtuvieron {len(eje)}.")
    return eje


def cargar_manrique() -> gpd.GeoDataFrame:
    """Obtiene exclusivamente el polígono territorial oficial de Comuna 3 - Manrique."""
    comunas = gpd.read_file(RUTA_COMUNAS)
    manrique = comunas.loc[
        (comunas["codigo"].astype(str).str.zfill(2) == "03")
        & (comunas["nombre"].astype(str).str.casefold() == "manrique")
    ].copy()
    if manrique.empty:
        raise ValueError("No se encontró el polígono oficial de Comuna 3 - Manrique.")
    if manrique.crs is None:
        raise ValueError("La capa de comunas no declara CRS.")
    return manrique.to_crs(CRS_METRICO)


def crear_corredor(eje: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, float]:
    """Genera el buffer y conserva únicamente la porción dentro de Manrique."""
    eje_unificado = eje.geometry.union_all()
    buffer_sin_recorte = eje_unificado.buffer(DISTANCIA_BUFFER_M)
    poligono_manrique = manrique.geometry.union_all()
    corredor = buffer_sin_recorte.intersection(poligono_manrique)
    if corredor.is_empty:
        raise ValueError("El recorte territorial produjo un corredor vacío.")
    salida = gpd.GeoDataFrame(
        {
            "nombre": ["Corredor analítico Carrera 45"],
            "distancia_buffer_m": [DISTANCIA_BUFFER_M],
            "territorio_proyecto": ["Comuna 3 - Manrique"],
        },
        geometry=[corredor],
        crs=CRS_METRICO,
    )
    return salida, float(buffer_sin_recorte.area)


def cargar_siniestros() -> tuple[pd.DataFrame, gpd.GeoDataFrame, dict[str, int]]:
    """Convierte lon/lat a puntos métricos solo en memoria, sin cambiar el CSV fuente."""
    siniestros = pd.read_csv(RUTA_SINIESTROS)
    requeridas = {"longitud", "latitud", "clase_siniestro", "gravedad_siniestro", "anio"}
    faltantes = requeridas - set(siniestros.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")
    longitud = pd.to_numeric(siniestros["longitud"], errors="coerce")
    latitud = pd.to_numeric(siniestros["latitud"], errors="coerce")
    coordenadas_nulas = longitud.isna() | latitud.isna()
    coordenadas_invalidas = (~coordenadas_nulas) & (~longitud.between(-180, 180) | ~latitud.between(-90, 90))
    validas = ~(coordenadas_nulas | coordenadas_invalidas)
    geometria = gpd.points_from_xy(longitud.where(validas), latitud.where(validas))
    puntos = gpd.GeoDataFrame(siniestros.copy(), geometry=geometria, crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)
    validacion = {
        "total": len(siniestros),
        "nulas": int(coordenadas_nulas.sum()),
        "invalidas": int(coordenadas_invalidas.sum()),
        "geometrias_nulas": int(puntos.geometry.isna().sum()),
        "geometrias_vacias": int(puntos.geometry.dropna().is_empty.sum()),
    }
    return siniestros, puntos, validacion


def seleccionar_siniestros(puntos: gpd.GeoDataFrame, eje: gpd.GeoDataFrame, corredor: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Selecciona puntos dentro o sobre el borde, sin spatial join ni duplicación de filas."""
    resultado = puntos.copy()
    eje_unificado = eje.geometry.union_all()
    validos = resultado.geometry.notna() & ~resultado.geometry.is_empty
    resultado["distancia_carrera45_m"] = pd.NA
    resultado.loc[validos, "distancia_carrera45_m"] = resultado.loc[validos].geometry.distance(eje_unificado)
    resultado["distancia_carrera45_m"] = pd.to_numeric(resultado["distancia_carrera45_m"], errors="coerce")
    geometria_corredor = corredor.geometry.iloc[0]
    # intersects incluye tanto interior como límite y se evalúa contra una sola geometría.
    dentro = validos & resultado.geometry.intersects(geometria_corredor)
    seleccionados = resultado.loc[dentro].copy()
    seleccionados["dentro_corredor_50m"] = True
    return seleccionados


def validar(corredor: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame, seleccionados: gpd.GeoDataFrame) -> dict[str, float | int | bool]:
    """Verifica territorio, geometría, ausencia de duplicación y distancia máxima."""
    geometria_corredor = corredor.geometry.iloc[0]
    fuera_manrique = geometria_corredor.difference(manrique.geometry.union_all()).area
    duplicados = int(seleccionados.index.duplicated().sum())
    distancia_maxima = float(seleccionados["distancia_carrera45_m"].max()) if len(seleccionados) else 0.0
    return {
        "crs_correcto": corredor.crs is not None and corredor.crs.to_epsg() == 9377,
        "geometrias_nulas": int(corredor.geometry.isna().sum()),
        "geometrias_vacias": int(corredor.geometry.is_empty.sum()),
        "geometrias_invalidas": int((~corredor.geometry.is_valid).sum()),
        "area_fuera_manrique_m2": float(fuera_manrique),
        "duplicados_seleccion": duplicados,
        "distancia_maxima_seleccionada_m": distancia_maxima,
        "distancias_fuera_tolerancia": int((seleccionados["distancia_carrera45_m"] > DISTANCIA_BUFFER_M + TOLERANCIA_M).sum()),
    }


def tabla_distribucion(datos: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Resume una columna categórica conservando también valores nulos si existieran."""
    return datos.groupby(columna, dropna=False).size().reset_index(name="cantidad").sort_values("cantidad", ascending=False)


def agregar_tabla(lineas: list[str], tabla: pd.DataFrame) -> None:
    """Inserta una tabla en texto manteniendo su legibilidad."""
    lineas.append(tabla.to_string(index=False)) if not tabla.empty else lineas.append("Sin registros.")


def crear_reporte(
    eje: gpd.GeoDataFrame,
    area_buffer_m2: float,
    corredor: gpd.GeoDataFrame,
    seleccionados: gpd.GeoDataFrame,
    validacion_puntos: dict[str, int],
    validacion: dict[str, float | int | bool],
    cantidad_sin_recorte: int,
) -> None:
    """Documenta el criterio metodológico y la comprobación frente al análisis previo."""
    total = validacion_puntos["total"]
    cantidad = len(seleccionados)
    diferencia_previa = cantidad - 644
    excluidos_por_recorte = cantidad_sin_recorte - cantidad
    lineas = [
        "REPORTE — CORREDOR ANALÍTICO CARRERA 45 DE 50 M",
        "",
        "Justificación metodológica: se adopta un corredor de 50 m para representar el entorno inmediato del eje vial.",
        "Entre 30 y 50 m se observaron 51 siniestros adicionales; entre 50 y 75 m, 227 adicionales.",
        "Los 50 m son una delimitación analítica del proyecto; no constituyen una norma oficial de ingeniería vial ni prueba de causalidad.",
        "La pertenencia al corredor representa proximidad espacial al eje de Carrera 45 y no implica causalidad entre la vía y el siniestro.",
        "",
        f"Longitud del eje definitivo: {eje.geometry.length.sum():.2f} m",
        f"Área del buffer antes del recorte territorial: {area_buffer_m2:.2f} m²",
        f"Área del corredor después del recorte a Manrique: {corredor.geometry.area.sum():.2f} m²",
        f"Cantidad total de siniestros de Manrique: {total}",
        f"Cantidad dentro del corredor: {cantidad}",
        f"Porcentaje dentro del corredor: {cantidad / total * 100:.2f}%",
        "",
        "VALIDACIÓN FRENTE AL ANÁLISIS PREVIO",
        "Resultado previo de distancia <= 50 m: 644 siniestros.",
        f"Resultado dentro del buffer de 50 m antes del recorte territorial: {cantidad_sin_recorte} siniestros.",
        f"Resultado de selección por corredor: {cantidad} siniestros.",
        f"Diferencia: {diferencia_previa} siniestros.",
        f"Siniestros excluidos exclusivamente por el recorte territorial a Manrique: {excluidos_por_recorte}.",
        "Los 40 siniestros de diferencia se encuentran a <= 50 m del eje, pero fuera de la porción del buffer permitida por el límite oficial de Manrique."
        if diferencia_previa == -40 and cantidad_sin_recorte == 644
        else "La diferencia se documenta mediante la comparación entre el buffer antes y después del recorte territorial.",
        "",
        "VALIDACIONES TÉCNICAS",
        f"CRS del corredor: {corredor.crs}",
        f"CRS correcto EPSG:9377: {validacion['crs_correcto']}",
        f"Geometrías nulas/vacías/inválidas del corredor: {validacion['geometrias_nulas']}/{validacion['geometrias_vacias']}/{validacion['geometrias_invalidas']}",
        f"Área del corredor fuera de Manrique: {validacion['area_fuera_manrique_m2']:.10f} m²",
        f"Filas duplicadas durante selección espacial: {validacion['duplicados_seleccion']}",
        f"Siniestros seleccionados a más de 50 m + tolerancia: {validacion['distancias_fuera_tolerancia']}",
        f"Distancia mínima/mediana/máxima seleccionada (m): {seleccionados['distancia_carrera45_m'].min():.2f} / {seleccionados['distancia_carrera45_m'].median():.2f} / {seleccionados['distancia_carrera45_m'].max():.2f}",
        "",
        "DISTRIBUCIÓN POR CLASE DE SINIESTRO",
    ]
    agregar_tabla(lineas, tabla_distribucion(seleccionados, "clase_siniestro"))
    lineas.extend(["", "DISTRIBUCIÓN POR GRAVEDAD DE SINIESTRO"])
    agregar_tabla(lineas, tabla_distribucion(seleccionados, "gravedad_siniestro"))
    lineas.extend(["", "DISTRIBUCIÓN POR AÑO"])
    agregar_tabla(lineas, tabla_distribucion(seleccionados, "anio"))
    RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
    RUTA_REPORTE.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def crear_mapa(manrique: gpd.GeoDataFrame, eje: gpd.GeoDataFrame, corredor: gpd.GeoDataFrame, seleccionados: gpd.GeoDataFrame) -> None:
    """Dibuja exclusivamente el territorio del proyecto, su eje, corredor y siniestros asociados."""
    fig, ax = plt.subplots(figsize=(9, 10), constrained_layout=True)
    manrique.plot(ax=ax, facecolor="#edf6f9", edgecolor="#1d3557", linewidth=1.1)
    corredor.plot(ax=ax, facecolor="#90e0ef", edgecolor="#00b4d8", alpha=0.6, linewidth=0.8)
    seleccionados.plot(ax=ax, color="#d62828", markersize=9, alpha=0.75)
    eje.plot(ax=ax, color="#003049", linewidth=2.2)
    handles = [
        Patch(facecolor="#edf6f9", edgecolor="#1d3557", label="Límite oficial de Manrique"),
        Patch(facecolor="#90e0ef", edgecolor="#00b4d8", label="Corredor analítico de 50 m"),
        Line2D([0], [0], marker="o", linestyle="", color="#d62828", markersize=6, label="Siniestros seleccionados"),
        Line2D([0], [0], color="#003049", linewidth=2.2, label="Eje definitivo Carrera 45"),
    ]
    ax.legend(handles=handles, loc="best")
    ax.set_title("Corredor analítico de 50 m — Carrera 45, Manrique")
    ax.set_xlabel("Coordenada X (m) — EPSG:9377")
    ax.set_ylabel("Coordenada Y (m) — EPSG:9377")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    fig.savefig(RUTA_MAPA, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Construye los productos del corredor y publica el resumen verificable."""
    for ruta in (RUTA_EJE, RUTA_SINIESTROS, RUTA_COMUNAS):
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el insumo requerido: {ruta}")
    eje = cargar_eje()
    manrique = cargar_manrique()
    corredor, area_buffer_m2 = crear_corredor(eje, manrique)
    _, puntos, validacion_puntos = cargar_siniestros()
    seleccionados = seleccionar_siniestros(puntos, eje, corredor)
    buffer_sin_recorte = eje.geometry.union_all().buffer(DISTANCIA_BUFFER_M)
    puntos_validos = puntos.geometry.notna() & ~puntos.geometry.is_empty
    cantidad_sin_recorte = int((puntos_validos & puntos.geometry.intersects(buffer_sin_recorte)).sum())
    validacion = validar(corredor, manrique, seleccionados)

    if any([not validacion["crs_correcto"], validacion["geometrias_nulas"], validacion["geometrias_vacias"], validacion["geometrias_invalidas"], validacion["area_fuera_manrique_m2"] > TOLERANCIA_M, validacion["duplicados_seleccion"], validacion["distancias_fuera_tolerancia"]]):
        raise ValueError(f"Falló una validación del corredor: {validacion}")

    RUTA_CORREDOR.parent.mkdir(parents=True, exist_ok=True)
    corredor.to_file(RUTA_CORREDOR, driver="GeoJSON")
    columnas_csv = [columna for columna in seleccionados.columns if columna != "geometry"]
    seleccionados[columnas_csv].to_csv(RUTA_SELECCIONADOS, index=False, encoding="utf-8")
    crear_reporte(eje, area_buffer_m2, corredor, seleccionados, validacion_puntos, validacion, cantidad_sin_recorte)
    crear_mapa(manrique, eje, corredor, seleccionados)

    print("CORREDOR ANALÍTICO DE CARRERA 45 — 50 M")
    print(f"CRS: {corredor.crs}")
    print(f"Área antes del recorte: {area_buffer_m2:.2f} m²")
    print(f"Área dentro de Manrique: {corredor.geometry.area.sum():.2f} m²")
    print(f"Siniestros seleccionados: {len(seleccionados)} de {validacion_puntos['total']} ({len(seleccionados) / validacion_puntos['total'] * 100:.2f}%)")
    print(f"Diferencia frente a distancia <= 50 m (644): {len(seleccionados) - 644}")
    print(f"Validaciones: {validacion}")
    print(f"Corredor: {RUTA_CORREDOR}")
    print(f"Siniestros: {RUTA_SELECCIONADOS}")
    print(f"Reporte: {RUTA_REPORTE}")
    print(f"Mapa: {RUTA_MAPA}")


if __name__ == "__main__":
    main()
