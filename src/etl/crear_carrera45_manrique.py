"""Construye el eje preliminar de Carrera 45 limitado al polígono de Manrique."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_MALLA = RAIZ_PROYECTO / "data" / "raw" / "malla_vial_medellin.geojson"
RUTA_COMUNAS = RAIZ_PROYECTO / "data" / "raw" / "comunas_medellin.geojson"
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "processed" / "carrera45_manrique_preliminar.geojson"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "reporte_carrera45_manrique_preliminar.txt"
RUTA_MAPA = RAIZ_PROYECTO / "reports" / "mapa_carrera45_manrique_preliminar.png"
CRS_METRICO = "EPSG:9377"
OID_REVISION_EJE = 13704


class Reporte:
    """Acumula resultados para consola y para el reporte persistente."""

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def agregar(self, texto: Any = "") -> None:
        contenido = str(texto)
        print(contenido)
        self.lineas.append(contenido)

    def guardar(self) -> None:
        RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
        RUTA_REPORTE.write_text("\n".join(self.lineas) + "\n", encoding="utf-8")


def buscar_columna(gdf: gpd.GeoDataFrame, nombre: str) -> str | None:
    """Busca campos reales sin depender de mayúsculas o minúsculas."""
    return next((columna for columna in gdf.columns if columna.lower() == nombre.lower()), None)


def validar_archivo(ruta: Path, nombre: str) -> None:
    """Evita procesar archivos inexistentes, vacíos o incompletos."""
    if not ruta.exists() or ruta.stat().st_size < 10:
        raise FileNotFoundError(f"La fuente {nombre} no existe o no es válida: {ruta}")


def cargar_manrique(reporte: Reporte) -> gpd.GeoDataFrame:
    """Carga exclusivamente el límite oficial de Comuna 3 - Manrique."""
    validar_archivo(RUTA_COMUNAS, "territorial de comunas")
    comunas = gpd.read_file(RUTA_COMUNAS)
    codigo = buscar_columna(comunas, "codigo")
    nombre = buscar_columna(comunas, "nombre")
    if codigo is None or nombre is None:
        raise ValueError("La capa de comunas no tiene los campos codigo y nombre.")
    if comunas.crs is None:
        raise ValueError("La capa de comunas no declara CRS.")

    manrique = comunas.loc[
        comunas[codigo].fillna("").astype(str).str.strip().eq("03")
        & comunas[nombre].fillna("").astype(str).str.strip().str.casefold().eq("manrique")
    ].copy()
    if len(manrique) != 1:
        raise ValueError(f"Se esperaba un único polígono para Comuna 3 - Manrique; se hallaron {len(manrique)}.")

    manrique = manrique.to_crs(CRS_METRICO)
    reporte.agregar("=== LÍMITE OFICIAL DE MANRIQUE ===")
    reporte.agregar(f"CRS: {manrique.crs}")
    reporte.agregar(f"Bounds: {manrique.total_bounds.tolist()}")
    reporte.agregar(f"Tipo de geometría: {manrique.geom_type.tolist()}")
    reporte.agregar(f"Geometrías nulas: {int(manrique.geometry.isna().sum())}")
    reporte.agregar(f"Geometrías vacías: {int(manrique.geometry.is_empty.sum())}")
    reporte.agregar(f"Geometrías inválidas: {int((~manrique.geometry.is_valid).sum())}")
    if manrique.geometry.isna().any() or manrique.geometry.is_empty.any() or (~manrique.geometry.is_valid).any():
        raise ValueError("El límite oficial de Manrique no es geométricamente válido.")
    return manrique


def cargar_malla_metrica(reporte: Reporte) -> gpd.GeoDataFrame:
    """Reinterpreta la malla en memoria como EPSG:4326 y la proyecta a EPSG:9377."""
    validar_archivo(RUTA_MALLA, "malla vial")
    malla = gpd.read_file(RUTA_MALLA)
    # No se toca el RAW: esta corrección responde a coordenadas reales en lon/lat.
    malla_metrica = malla.set_crs("EPSG:4326", allow_override=True).to_crs(CRS_METRICO)
    reporte.agregar("\n=== MALLA VIAL EN MEMORIA ===")
    reporte.agregar(f"CRS de análisis: {malla_metrica.crs}")
    reporte.agregar(f"Bounds reproyectados: {malla_metrica.total_bounds.tolist()}")
    return malla_metrica


def es_vacio(serie: pd.Series) -> pd.Series:
    """Reconoce nulos, cadenas vacías y cadenas formadas solo por espacios."""
    return serie.isna() | serie.astype(str).str.strip().eq("")


def seleccionar_candidatos(malla: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Selecciona el eje principal: únicamente Carrera 45, sin variantes ni calles."""
    tipo_via = buscar_columna(malla, "tipo_via")
    numero_via = buscar_columna(malla, "numero_via")
    apendice = buscar_columna(malla, "apendice_via")
    if tipo_via is None or numero_via is None or apendice is None:
        raise ValueError("La malla no tiene tipo_via, numero_via y apendice_via para seleccionar Carrera 45.")
    numero = pd.to_numeric(malla[numero_via], errors="coerce")
    # Un apéndice no vacío identifica variantes como CR 45A, CR 45B, etc.;
    # no se incorporan automáticamente a esta primera versión del eje principal.
    return malla.loc[
        malla[tipo_via].eq("CR") & numero.eq(45) & es_vacio(malla[apendice])
    ].copy()


def recortar_a_manrique(candidatos: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Conserva únicamente la porción de cada segmento que intersecta Manrique."""
    poligono = manrique.geometry.union_all()
    resultado = candidatos.copy()
    resultado["longitud_geometrica_original_m"] = resultado.geometry.length
    resultado["_geometria_recortada"] = resultado.geometry.intersection(poligono)
    resultado["longitud_dentro_manrique_m"] = resultado["_geometria_recortada"].length
    resultado["porcentaje_dentro_manrique"] = (
        resultado["longitud_dentro_manrique_m"]
        .div(resultado["longitud_geometrica_original_m"])
        .mul(100)
    )
    resultado = resultado.loc[~resultado["_geometria_recortada"].is_empty].copy()
    # Se reemplaza únicamente la geometría activa de la copia procesada; el RAW queda intacto.
    resultado["geometry"] = resultado["_geometria_recortada"]
    resultado = resultado.drop(columns="_geometria_recortada")
    resultado = gpd.GeoDataFrame(resultado, geometry="geometry", crs=candidatos.crs)
    return resultado


def preparar_salida(resultado: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Conserva trazabilidad y añade exclusivamente los campos de control solicitados."""
    objectid = buscar_columna(resultado, "objectid")
    campos = [
        columna for columna in (
            objectid, buscar_columna(resultado, "tipo_via"), buscar_columna(resultado, "numero_via"),
            buscar_columna(resultado, "label"), buscar_columna(resultado, "nombre_comun"),
            buscar_columna(resultado, "apendice_via"), buscar_columna(resultado, "orientacion_via"),
            buscar_columna(resultado, "longitud"),
        ) if columna is not None
    ]
    salida = resultado[campos + ["geometry"]].copy()
    comuna = buscar_columna(resultado, "comuna")
    salida["comuna_original_malla"] = resultado[comuna] if comuna else pd.NA
    salida["longitud_original"] = resultado[buscar_columna(resultado, "longitud")] if buscar_columna(resultado, "longitud") else pd.NA
    salida["longitud_geometrica_original_m"] = resultado["longitud_geometrica_original_m"]
    salida["longitud_dentro_manrique_m"] = resultado["longitud_dentro_manrique_m"]
    salida["porcentaje_dentro_manrique"] = resultado["porcentaje_dentro_manrique"]
    salida["territorio_proyecto"] = "Comuna 3 - Manrique"
    salida["requiere_revision_eje"] = resultado[objectid].eq(OID_REVISION_EJE) if objectid else False
    return gpd.GeoDataFrame(salida, geometry="geometry", crs=resultado.crs)


def validar_resultado(resultado: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame) -> dict[str, Any]:
    """Comprueba CRS, geometrías y que la intersección no salga del polígono oficial."""
    poligono = manrique.geometry.union_all()
    # difference() permite aceptar segmentos que terminan exactamente sobre el borde,
    # pero detecta cualquier tramo con longitud fuera del territorio oficial.
    longitud_fuera = resultado.geometry.difference(poligono).length
    # Un milímetro tolera residuos de precisión de la operación de intersección,
    # sin aceptar un tramo territorialmente externo.
    fuera = int(longitud_fuera.gt(1e-3).sum())
    return {
        "crs": str(resultado.crs),
        "geometrias_nulas": int(resultado.geometry.isna().sum()),
        "geometrias_vacias": int(resultado.geometry.is_empty.sum()),
        "geometrias_invalidas": int((~resultado.geometry.is_valid).sum()),
        "geometrias_fuera_manrique": fuera,
        "longitud_total_m": float(resultado.geometry.length.sum()),
    }


def generar_reporte(
    reporte: Reporte,
    candidatos: gpd.GeoDataFrame,
    resultado: gpd.GeoDataFrame,
    validacion: dict[str, Any],
) -> None:
    """Documenta inclusión, recortes y pendientes sin declarar un corredor definitivo."""
    objectid = buscar_columna(resultado, "objectid")
    ids_incluidos = [int(valor) for valor in resultado[objectid].tolist()] if objectid else []
    fuera_ids = []
    if objectid:
        fuera_ids = [int(valor) for valor in candidatos.loc[~candidatos[objectid].isin(resultado[objectid]), objectid].tolist()]

    reporte.agregar("\n=== REPORTE: CARRERA 45 - MANRIQUE (PRELIMINAR) ===")
    reporte.agregar(f"Segmentos originales candidatos: {len(candidatos)}")
    reporte.agregar(f"Segmentos que intersectan Manrique: {len(resultado)}")
    reporte.agregar(f"Longitud total recortada dentro de Manrique: {validacion['longitud_total_m']:.2f} m")
    reporte.agregar(f"Objectid incluidos: {ids_incluidos}")
    reporte.agregar(f"Objectid fuera de Manrique: {fuera_ids}")

    tabla = resultado[[
        objectid, "comuna_original_malla", "longitud_dentro_manrique_m",
        "porcentaje_dentro_manrique", "requiere_revision_eje",
    ]].copy()
    tabla["longitud_dentro_manrique_m"] = tabla["longitud_dentro_manrique_m"].round(2)
    tabla["porcentaje_dentro_manrique"] = tabla["porcentaje_dentro_manrique"].round(2)
    reporte.agregar("\nComuna original, longitud y porcentaje dentro de Manrique:")
    reporte.agregar(tabla.to_string(index=False))

    parciales = resultado.loc[resultado["porcentaje_dentro_manrique"] < 99.999]
    contenidos = resultado.loc[resultado["porcentaje_dentro_manrique"] >= 99.999]
    revision = resultado.loc[resultado["requiere_revision_eje"]]
    reporte.agregar(f"\nSegmentos parcialmente recortados: {len(parciales)}")
    reporte.agregar(f"Segmentos totalmente contenidos: {len(contenidos)}")
    reporte.agregar(f"Segmentos marcados para revisión: {len(revision)}")
    reporte.agregar(f"CRS resultado: {validacion['crs']}")
    reporte.agregar(f"Geometrías nulas: {validacion['geometrias_nulas']}")
    reporte.agregar(f"Geometrías vacías: {validacion['geometrias_vacias']}")
    reporte.agregar(f"Geometrías inválidas: {validacion['geometrias_invalidas']}")
    reporte.agregar(f"Geometrías fuera de Manrique: {validacion['geometrias_fuera_manrique']}")
    reporte.agregar("Resultado PRELIMINAR: no constituye aún el corredor definitivo.")


def crear_mapa(manrique: gpd.GeoDataFrame, resultado: gpd.GeoDataFrame) -> None:
    """Muestra solo Manrique, el eje recortado y el segmento marcado para revisión."""
    fig, ax = plt.subplots(figsize=(10, 10), constrained_layout=True)
    manrique.plot(ax=ax, facecolor="#e8f1f2", edgecolor="#1d3557", linewidth=1.5)
    resultado.plot(ax=ax, color="#0077b6", linewidth=2.5, label="Carrera 45 preliminar")
    revision = resultado.loc[resultado["requiere_revision_eje"]]
    if not revision.empty:
        revision.plot(ax=ax, color="#d62828", linewidth=3.5, label="Requiere revisión de eje")

    # El tramo destacado conserva una etiqueta visible; rotular todos los segmentos
    # cortos superpondría texto y dificultaría el diagnóstico.
    for _, fila in revision.iterrows():
        punto = fila.geometry.representative_point()
        ax.annotate(
            f"OID {int(fila['objectid'])}",
            (punto.x, punto.y),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.8},
        )

    ax.set_title("Carrera 45 dentro del límite oficial de Comuna 3 - Manrique\nResultado preliminar")
    ax.set_xlabel("Coordenada X (m) — EPSG:9377")
    ax.set_ylabel("Coordenada Y (m) — EPSG:9377")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend(loc="best")
    RUTA_MAPA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(RUTA_MAPA, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Genera el GeoJSON y reporte preliminares, conservando intactos ambos RAW."""
    reporte = Reporte()
    try:
        manrique = cargar_manrique(reporte)
        malla = cargar_malla_metrica(reporte)
        candidatos = seleccionar_candidatos(malla)
        recortados = recortar_a_manrique(candidatos, manrique)
        resultado = preparar_salida(recortados)
        validacion = validar_resultado(resultado, manrique)
        if any(validacion[clave] for clave in ("geometrias_nulas", "geometrias_vacias", "geometrias_invalidas", "geometrias_fuera_manrique")):
            raise ValueError(f"La salida preliminar no superó validaciones: {validacion}")

        RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
        resultado.to_file(RUTA_SALIDA, driver="GeoJSON")
        crear_mapa(manrique, resultado)
        generar_reporte(reporte, candidatos, resultado, validacion)
        reporte.agregar(f"\nGeoJSON preliminar guardado en: {RUTA_SALIDA}")
        reporte.agregar(f"Mapa preliminar guardado en: {RUTA_MAPA}")
    except (FileNotFoundError, ValueError, OSError) as error:
        reporte.agregar(f"\nNo se generó el eje preliminar: {error}")
    finally:
        reporte.guardar()
        print(f"\nReporte guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()
