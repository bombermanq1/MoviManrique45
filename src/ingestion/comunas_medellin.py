"""Descarga y valida la capa oficial de Comunas y Corregimientos de Medellín."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import requests


URL_CAPA = (
    "https://www.medellin.gov.co/servidormapas/rest/services/ServiciosCatastro/"
    "Base_Catastral/MapServer/0"
)
TIEMPO_ESPERA = 60
ENCABEZADOS_HTTP = {
    "User-Agent": "MoviManrique45/1.0 (consulta académica de datos abiertos)",
    "Accept": "application/json, application/geo+json",
}
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "raw" / "comunas_medellin.geojson"


def solicitar_json(url: str, parametros: dict[str, Any]) -> dict[str, Any]:
    """Consulta ArcGIS y presenta de forma explícita errores HTTP o del servicio."""
    respuesta = requests.get(
        url,
        params=parametros,
        headers=ENCABEZADOS_HTTP,
        timeout=TIEMPO_ESPERA,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    if "error" in datos:
        error = datos["error"]
        raise RuntimeError(
            f"ArcGIS devolvió error {error.get('code', '')}: "
            f"{error.get('message', error)}"
        )
    return datos


def obtener_metadatos() -> dict[str, Any]:
    """Obtiene la descripción oficial de la capa antes de descargar entidades."""
    return solicitar_json(URL_CAPA, {"f": "json"})


def consultar_total_registros() -> int:
    """Consulta el total publicado, sin descargar aún las geometrías."""
    datos = solicitar_json(
        f"{URL_CAPA}/query",
        {"f": "json", "where": "1=1", "returnCountOnly": "true"},
    )
    return int(datos["count"])


def descargar_geojson_paginado(maximo_registros: int) -> dict[str, Any]:
    """Descarga todos los atributos y polígonos mediante páginas GeoJSON."""
    entidades: list[dict[str, Any]] = []
    desplazamiento = 0

    while True:
        pagina = solicitar_json(
            f"{URL_CAPA}/query",
            {
                "f": "geojson",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "resultOffset": desplazamiento,
                "resultRecordCount": maximo_registros,
                "orderByFields": "objectid ASC",
            },
        )
        entidades_pagina = pagina.get("features", [])
        if not entidades_pagina:
            break

        entidades.extend(entidades_pagina)
        print(f"Registros descargados: {len(entidades)}")
        if len(entidades_pagina) < maximo_registros:
            break
        desplazamiento += len(entidades_pagina)

    # Se conservan atributos y coordenadas de la respuesta GeoJSON, sin reproyección.
    return {"type": "FeatureCollection", "features": entidades}


def buscar_columna(gdf: gpd.GeoDataFrame, nombre: str) -> str | None:
    """Encuentra un campo real sin depender de mayúsculas o minúsculas."""
    return next((columna for columna in gdf.columns if columna.lower() == nombre.lower()), None)


def mostrar_valores(gdf: gpd.GeoDataFrame, nombre: str) -> None:
    """Muestra valores publicados de un atributo solicitado, incluida la ausencia."""
    columna = buscar_columna(gdf, nombre)
    if columna is None:
        print(f"No existe la columna {nombre}.")
        return
    print(f"Valores de {columna}: {gdf[columna].unique().tolist()}")


def validar_capa(
    gdf: gpd.GeoDataFrame, metadatos: dict[str, Any], total_oficial: int
) -> None:
    """Muestra estructura y calidad sin alterar las geometrías recibidas."""
    referencia = metadatos.get("extent", {}).get("spatialReference", {})
    bounds = gdf.total_bounds
    coordenadas_geograficas = (
        abs(bounds[0]) <= 180
        and abs(bounds[2]) <= 180
        and abs(bounds[1]) <= 90
        and abs(bounds[3]) <= 90
    )

    print("\n=== VALIDACIÓN DE COMUNAS Y CORREGIMIENTOS ===")
    print(f"Cantidad oficial de registros: {total_oficial}")
    print(f"Cantidad de registros descargados: {len(gdf)}")
    print(f"Columnas: {gdf.columns.tolist()}")
    print(f"CRS publicado por ArcGIS: {referencia}")
    print(f"CRS detectado en GeoDataFrame: {gdf.crs}")
    print(f"Bounds de geometrías recibidas: {bounds.tolist()}")
    print(
        "Coordenadas con apariencia geográfica (longitud/latitud): "
        f"{coordenadas_geograficas}"
    )
    print(f"Tipos de geometría: {gdf.geom_type.value_counts(dropna=False).to_dict()}")
    print(f"Geometrías nulas: {int(gdf.geometry.isna().sum())}")
    print(f"Geometrías vacías: {int(gdf.geometry.is_empty.sum())}")
    print(f"Geometrías inválidas: {int((gdf.geometry.notna() & ~gdf.geometry.is_valid).sum())}")

    for nombre in ("comuna", "nombre"):
        mostrar_valores(gdf, nombre)


def comprobar_comuna_manrique(gdf: gpd.GeoDataFrame) -> None:
    """Comprueba con atributos publicados si está incluida la Comuna 3 - Manrique."""
    comuna = buscar_columna(gdf, "comuna")
    nombre = buscar_columna(gdf, "nombre")

    if comuna is None or nombre is None:
        print("No fue posible comprobar Comuna 3 / Manrique: faltan comuna o nombre.")
        return

    mascara_manrique = gdf[nombre].fillna("").astype(str).str.contains(
        "MANRIQUE", case=False, regex=False
    )
    encontrados = gdf.loc[mascara_manrique]
    print("\n=== COMPROBACIÓN: COMUNA 3 - MANRIQUE ===")
    if encontrados.empty:
        print("No se encontró un registro con 'MANRIQUE' en el nombre publicado.")
        return

    columnas = [comuna, nombre]
    print("Registros que contienen MANRIQUE (con valor de comuna publicado):")
    print(encontrados[columnas].to_string(index=False))


def guardar_geojson_original(geojson: dict[str, Any]) -> None:
    """Guarda la respuesta GeoJSON agregada sin transformar atributos ni geometrías."""
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with RUTA_SALIDA.open("w", encoding="utf-8") as archivo:
        json.dump(geojson, archivo, ensure_ascii=False)


def main() -> None:
    """Ejecuta descarga, validación y guardado RAW de la fuente oficial."""
    try:
        metadatos = obtener_metadatos()
        total_oficial = consultar_total_registros()
        maximo_registros = int(metadatos.get("maxRecordCount", 2000))
        geojson = descargar_geojson_paginado(maximo_registros)
    except requests.RequestException as error:
        print(f"Error HTTP al consultar la capa oficial: {error}")
        return
    except (RuntimeError, KeyError, ValueError) as error:
        print(f"Error al procesar la respuesta ArcGIS: {error}")
        return

    gdf = gpd.GeoDataFrame.from_features(geojson["features"])
    guardar_geojson_original(geojson)
    validar_capa(gdf, metadatos, total_oficial)
    comprobar_comuna_manrique(gdf)
    print(f"\nCapa RAW guardada en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
