"""Diagnóstico geométrico de segmentos de Carrera 45 dentro de Manrique."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_MALLA = RAIZ_PROYECTO / "data" / "raw" / "malla_vial_medellin.geojson"
RUTA_COMUNAS = RAIZ_PROYECTO / "data" / "raw" / "comunas_medellin.geojson"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "validacion_carrera45_manrique.txt"
CRS_METRICO = "EPSG:9377"
OIDS_HUECOS = [24568, 23780, 25862, 26016, 21844]
OIDS_ESPECIALES = [13704, 710]


class Reporte:
    """Registra los resultados en consola y en un reporte de texto."""

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
    """Obtiene un nombre de campo real sin depender de mayúsculas/minúsculas."""
    return next((columna for columna in gdf.columns if columna.lower() == nombre.lower()), None)


def validar_archivo_geojson(ruta: Path, nombre: str) -> None:
    """Evita ejecutar cálculos espaciales sobre archivos vacíos o inexistentes."""
    if not ruta.exists():
        raise FileNotFoundError(f"No existe la fuente {nombre}: {ruta}")
    if ruta.stat().st_size < 10:
        raise ValueError(
            f"La fuente {nombre} no contiene un GeoJSON válido (tamaño: "
            f"{ruta.stat().st_size} bytes)."
        )


def cargar_malla_metrica() -> gpd.GeoDataFrame:
    """Interpreta la malla como EPSG:4326 en memoria y la proyecta para medir."""
    validar_archivo_geojson(RUTA_MALLA, "malla vial")
    malla = gpd.read_file(RUTA_MALLA)
    # El archivo RAW no se modifica: su CRS se corrige exclusivamente en esta copia.
    return malla.set_crs("EPSG:4326", allow_override=True).to_crs(CRS_METRICO)


def cargar_poligono_manrique(reporte: Reporte) -> gpd.GeoDataFrame:
    """Carga y valida el límite oficial de Manrique con coordenadas métricas reales."""
    validar_archivo_geojson(RUTA_COMUNAS, "límite territorial de comunas")
    comunas = gpd.read_file(RUTA_COMUNAS)
    codigo = buscar_columna(comunas, "codigo")
    nombre = buscar_columna(comunas, "nombre")
    if codigo is None or nombre is None:
        raise ValueError("La capa territorial no contiene los campos codigo y nombre requeridos.")

    reporte.agregar("=== VALIDACIÓN DEL LÍMITE TERRITORIAL ===")
    reporte.agregar(f"CRS declarado/detectado: {comunas.crs}")
    reporte.agregar(f"Bounds: {comunas.total_bounds.tolist()}")
    reporte.agregar(f"Tipos geométricos: {comunas.geom_type.value_counts(dropna=False).to_dict()}")

    mascara_codigo = comunas[codigo].fillna("").astype(str).str.strip().eq("03")
    manrique = comunas.loc[mascara_codigo].copy()
    if manrique.empty:
        raise ValueError("No existe un registro territorial con codigo == '03'.")

    reporte.agregar(f"Registros con codigo '03': {len(manrique)}")
    reporte.agregar(f"Nombre publicado: {manrique[nombre].tolist()}")
    reporte.agregar(f"Geometrías nulas: {int(manrique.geometry.isna().sum())}")
    reporte.agregar(f"Geometrías vacías: {int(manrique.geometry.is_empty.sum())}")
    reporte.agregar(
        f"Geometrías inválidas: {int((manrique.geometry.notna() & ~manrique.geometry.is_valid).sum())}"
    )
    if manrique.geometry.isna().any() or manrique.geometry.is_empty.any() or (~manrique.geometry.is_valid).any():
        raise ValueError("El polígono de Manrique no supera las validaciones geométricas.")
    if manrique.crs is None:
        raise ValueError("La capa territorial no declara CRS; no es posible validar distancias en metros.")
    return manrique.to_crs(CRS_METRICO)


def es_vacio(serie: pd.Series) -> pd.Series:
    """Reconoce nulos, cadenas vacías y cadenas compuestas únicamente por espacios."""
    return serie.isna() | serie.astype(str).str.strip().eq("")


def candidatos_carrera45(malla: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Identifica representaciones potenciales de Carrera 45 sin usar comuna como criterio."""
    tipo_via = buscar_columna(malla, "tipo_via")
    numero_via = buscar_columna(malla, "numero_via")
    via_principal = buscar_columna(malla, "via_principal")
    via_generadora = buscar_columna(malla, "via_generadora")
    label = buscar_columna(malla, "label")
    objectid = buscar_columna(malla, "objectid")

    if not all((tipo_via, numero_via, objectid)):
        raise ValueError("La malla vial no contiene objectid, tipo_via y numero_via.")

    mascara = malla[tipo_via].eq("CR") & malla[numero_via].eq(45)
    if via_principal:
        mascara |= malla[via_principal].fillna("").astype(str).str.strip().str.startswith("45")
    if via_generadora:
        mascara |= malla[via_generadora].fillna("").astype(str).str.strip().eq("45")
    if label:
        mascara |= malla[label].fillna("").astype(str).str.contains("CR 45", case=False, regex=False)
    mascara |= malla[objectid].isin(OIDS_ESPECIALES)
    return malla.loc[mascara].copy()


def es_transversal(geometria) -> bool:
    """Marca como dudoso un tramo cuya extensión este-oeste supera la norte-sur."""
    xmin, ymin, xmax, ymax = geometria.bounds
    return (xmax - xmin) > (ymax - ymin)


def calcular_interseccion(
    candidatos: gpd.GeoDataFrame, manrique: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Calcula longitudes dentro del límite oficial sin cambiar la malla original."""
    poligono = manrique.geometry.union_all()
    resultado = candidatos.copy()
    resultado["intersecta_manrique"] = resultado.geometry.intersects(poligono)
    resultado["longitud_geometrica_m"] = resultado.geometry.length
    resultado["longitud_dentro_manrique_m"] = resultado.geometry.intersection(poligono).length
    resultado["porcentaje_dentro_manrique"] = (
        resultado["longitud_dentro_manrique_m"]
        .div(resultado["longitud_geometrica_m"])
        .mul(100)
    )
    return resultado


def columnas_salida(gdf: gpd.GeoDataFrame) -> list[str]:
    """Define columnas publicadas para la tabla diagnóstica solicitada."""
    solicitadas = [
        "objectid", "comuna", "label", "nombre_comun", "apendice_via",
        "orientacion_via", "longitud", "intersecta_manrique",
        "longitud_geometrica_m", "longitud_dentro_manrique_m",
        "porcentaje_dentro_manrique",
    ]
    return [columna for columna in solicitadas if columna in gdf.columns]


def mostrar_grupo(reporte: Reporte, titulo: str, gdf: gpd.GeoDataFrame) -> None:
    """Incluye una tabla compacta de segmentos en el reporte de diagnóstico."""
    reporte.agregar(f"\n=== {titulo} ({len(gdf)}) ===")
    if gdf.empty:
        reporte.agregar("Sin segmentos en esta categoría.")
        return
    tabla = gdf[columnas_salida(gdf)].copy()
    for columna in (
        "longitud_geometrica_m", "longitud_dentro_manrique_m", "porcentaje_dentro_manrique"
    ):
        if columna in tabla:
            tabla[columna] = tabla[columna].round(2)
    reporte.agregar(tabla.to_string(index=False))


def generar_reporte(resultado: gpd.GeoDataFrame, reporte: Reporte) -> None:
    """Organiza categorías territoriales sin decidir todavía el corredor definitivo."""
    comuna = buscar_columna(resultado, "comuna")
    objectid = buscar_columna(resultado, "objectid")
    apendice = buscar_columna(resultado, "apendice_via")
    tipo_via = buscar_columna(resultado, "tipo_via")

    en_comuna03 = resultado[comuna].fillna("").astype(str).str.strip().eq("03") if comuna else False
    en_comuna04 = resultado[comuna].fillna("").astype(str).str.strip().eq("04") if comuna else False
    dentro = resultado["intersecta_manrique"]

    mostrar_grupo(reporte, "A) Registrados como comuna 03 e intersectan Manrique", resultado.loc[en_comuna03 & dentro])
    mostrar_grupo(reporte, "B) Registrados como comuna 04 e intersectan Manrique", resultado.loc[en_comuna04 & dentro])
    mostrar_grupo(reporte, "C) Candidatos completamente fuera de Manrique", resultado.loc[~dentro])

    especiales = pd.Series(False, index=resultado.index)
    if apendice:
        especiales |= ~es_vacio(resultado[apendice])
    if objectid:
        especiales |= resultado[objectid].isin(OIDS_ESPECIALES)
    if tipo_via:
        especiales |= resultado[tipo_via].ne("CR")
    especiales |= resultado.geometry.map(es_transversal)
    mostrar_grupo(reporte, "D) Segmentos especiales o dudosos", resultado.loc[especiales])

    if objectid:
        huecos = resultado.loc[resultado[objectid].isin(OIDS_HUECOS)]
        mostrar_grupo(reporte, "Revisión de segmentos que rellenaban huecos", huecos)

    reporte.agregar(
        "\nConclusión: la pertenencia territorial se describe mediante la intersección "
        "con el polígono oficial; este reporte no crea ni decide un corredor definitivo."
    )


def main() -> None:
    """Ejecuta el diagnóstico territorial manteniendo intactas ambas fuentes RAW."""
    reporte = Reporte()
    reporte.agregar("VALIDACIÓN GEOMÉTRICA DE CARRERA 45 EN COMUNA 3 - MANRIQUE")
    try:
        manrique = cargar_poligono_manrique(reporte)
        malla = cargar_malla_metrica()
        reporte.agregar("\n=== MALLA VIAL PREPARADA EN MEMORIA ===")
        reporte.agregar(f"CRS de análisis: {malla.crs}")
        reporte.agregar(f"Bounds de malla proyectada: {malla.total_bounds.tolist()}")
        resultado = calcular_interseccion(candidatos_carrera45(malla), manrique)
        reporte.agregar(f"Segmentos potenciales de Carrera 45: {len(resultado)}")
        generar_reporte(resultado, reporte)
    except (FileNotFoundError, ValueError, OSError) as error:
        reporte.agregar(f"\nDiagnóstico no ejecutado: {error}")
        reporte.agregar(
            "No se realizaron intersecciones ni se generaron resultados territoriales "
            "porque la fuente oficial de comunas no es legible."
        )
    finally:
        reporte.guardar()
        print(f"\nReporte guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()
