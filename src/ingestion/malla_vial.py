"""Ingesta y perfilamiento inicial de la malla vial oficial de Medellín."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import requests


URL_CAPA = (
    "https://www.medellin.gov.co/servidormapas/rest/services/"
    "vivienda_ciudad_terri/VM_Base_overview/MapServer/1"
)
TIEMPO_ESPERA = 60
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "raw" / "malla_vial_medellin.geojson"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "perfilamiento_malla_vial.txt"


class Reporte:
    """Conserva un resumen que se muestra en consola y se guarda en un archivo."""

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def agregar(self, texto: object = "") -> None:
        """Imprime y almacena el contenido de una sección del perfilamiento."""
        contenido = str(texto)
        print(contenido)
        self.lineas.append(contenido)

    def guardar(self) -> None:
        """Crea reports cuando sea necesario y escribe el reporte de perfilamiento."""
        RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
        RUTA_REPORTE.write_text("\n".join(self.lineas) + "\n", encoding="utf-8")


def solicitar_json(url: str, parametros: dict[str, Any]) -> dict[str, Any]:
    """Consulta ArcGIS y convierte errores HTTP o propios del servicio en mensajes claros."""
    respuesta = requests.get(url, params=parametros, timeout=TIEMPO_ESPERA)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if "error" in datos:
        error = datos["error"]
        raise RuntimeError(
            f"ArcGIS devolvió un error {error.get('code', '')}: "
            f"{error.get('message', error)}"
        )
    return datos


def obtener_metadatos(url_capa: str) -> dict[str, Any]:
    """Obtiene metadatos oficiales de la capa antes de descargar entidades."""
    return solicitar_json(url_capa, {"f": "json"})


def consultar_total_registros(url_capa: str) -> int:
    """Consulta el total oficial de registros sin descargar todavía las geometrías."""
    respuesta = solicitar_json(
        f"{url_capa}/query",
        {"f": "json", "where": "1=1", "returnCountOnly": "true"},
    )
    return int(respuesta["count"])


def obtener_crs(metadatos: dict[str, Any]) -> str | None:
    """Construye un CRS EPSG a partir de la referencia espacial publicada por ArcGIS."""
    referencia = metadatos.get("extent", {}).get("spatialReference", {})
    wkid = referencia.get("latestWkid") or referencia.get("wkid")
    return f"EPSG:{wkid}" if wkid else None


def descargar_geojson_paginado(
    url_capa: str, maximo_registros: int
) -> list[dict[str, Any]]:
    """Descarga todas las entidades GeoJSON mediante resultOffset y resultRecordCount."""
    entidades: list[dict[str, Any]] = []
    desplazamiento = 0
    url_query = f"{url_capa}/query"

    while True:
        parametros = {
            "f": "geojson",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "resultOffset": desplazamiento,
            "resultRecordCount": maximo_registros,
            # El orden estable evita que las páginas dependan del orden interno del servicio.
            "orderByFields": "objectid ASC",
        }
        pagina = solicitar_json(url_query, parametros)
        entidades_pagina = pagina.get("features", [])

        if not entidades_pagina:
            break

        entidades.extend(entidades_pagina)
        print(f"Registros descargados: {len(entidades)}")

        if len(entidades_pagina) < maximo_registros:
            break
        desplazamiento += len(entidades_pagina)

    return entidades


def convertir_a_geodataframe(
    entidades: list[dict[str, Any]], crs: str | None
) -> gpd.GeoDataFrame:
    """Convierte las entidades GeoJSON en un GeoDataFrame sin modificar atributos."""
    return gpd.GeoDataFrame.from_features(entidades, crs=crs)


def campos_candidatos(columnas: list[str]) -> list[str]:
    """Encuentra campos potencialmente útiles sin asumir cuál identifica la Carrera 45."""
    palabras_clave = ("nombre", "name", "label", "tipo", "via", "direccion")
    return [
        columna
        for columna in columnas
        if any(palabra in columna.lower() for palabra in palabras_clave)
    ]


def resumir_valores_candidatos(gdf: gpd.GeoDataFrame, columnas: list[str]) -> list[str]:
    """Entrega una muestra razonable de valores existentes para los campos candidatos."""
    resumen: list[str] = []
    for columna in columnas:
        valores_presentes = gdf.loc[gdf[columna].notna(), columna].astype(str)
        muestra = valores_presentes.unique()[:10].tolist()
        resumen.append(
            f"{columna} | valores únicos: {gdf[columna].nunique(dropna=True)} | "
            f"muestra: {muestra}"
        )
    return resumen


def perfilar_malla(
    gdf: gpd.GeoDataFrame, metadatos: dict[str, Any], total_oficial: int, reporte: Reporte
) -> None:
    """Registra estructura, CRS, calidad geométrica y campos para exploración posterior."""
    referencia = metadatos.get("extent", {}).get("spatialReference", {})
    campos_api = metadatos.get("fields", [])
    geometria = gdf.geometry
    geometria_nula = int(geometria.isna().sum())
    geometria_vacia = int(geometria.notna().sum() and geometria.is_empty.sum())
    geometria_invalida = int((geometria.notna() & ~geometria.is_valid).sum())

    reporte.agregar("PERFILAMIENTO DE MALLA VIAL OFICIAL DE MEDELLÍN")
    reporte.agregar(f"Nombre de la capa: {metadatos.get('name')}")
    reporte.agregar(f"Tipo de geometría: {metadatos.get('geometryType')}")
    reporte.agregar(f"Sistema de coordenadas publicado: {referencia}")
    reporte.agregar(f"CRS asignado al GeoDataFrame: {gdf.crs}")
    reporte.agregar(f"Máximo de registros por consulta: {metadatos.get('maxRecordCount')}")
    reporte.agregar(f"Cantidad total oficial de registros: {total_oficial}")
    reporte.agregar(f"Cantidad de registros descargados: {len(gdf)}")

    reporte.agregar("\nCampos disponibles según metadatos:")
    for campo in campos_api:
        reporte.agregar(
            f"- {campo.get('name')} | tipo: {campo.get('type')} | "
            f"alias: {campo.get('alias')}"
        )

    reporte.agregar("\nColumnas disponibles en el GeoDataFrame:")
    reporte.agregar(", ".join(gdf.columns))
    reporte.agregar("\nCalidad de geometrías:")
    reporte.agregar(f"Geometrías nulas: {geometria_nula}")
    reporte.agregar(f"Geometrías vacías: {geometria_vacia}")
    reporte.agregar(f"Geometrías inválidas: {geometria_invalida}")

    candidatas = campos_candidatos(gdf.columns.tolist())
    reporte.agregar("\nCampos candidatos para explorar Carrera 45 (sin aplicar filtros):")
    if candidatas:
        for fila in resumir_valores_candidatos(gdf, candidatas):
            reporte.agregar(f"- {fila}")
    else:
        reporte.agregar("No se identificaron campos candidatos por nombre.")


def main() -> None:
    """Orquesta metadatos, conteo, descarga paginada, validación y guardado RAW."""
    reporte = Reporte()
    try:
        metadatos = obtener_metadatos(URL_CAPA)
        total_oficial = consultar_total_registros(URL_CAPA)
        maximo_registros = int(metadatos.get("maxRecordCount", 2000))
        entidades = descargar_geojson_paginado(URL_CAPA, maximo_registros)
        malla_vial = convertir_a_geodataframe(entidades, obtener_crs(metadatos))
    except requests.RequestException as error:
        mensaje = f"Error HTTP al consultar la API de malla vial: {error}"
        print(mensaje)
        reporte.agregar(mensaje)
        reporte.guardar()
        return
    except (RuntimeError, ValueError, KeyError) as error:
        mensaje = f"Error al procesar la respuesta de ArcGIS: {error}"
        print(mensaje)
        reporte.agregar(mensaje)
        reporte.guardar()
        return

    perfilar_malla(malla_vial, metadatos, total_oficial, reporte)
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    malla_vial.to_file(RUTA_SALIDA, driver="GeoJSON")
    reporte.agregar(f"\nFuente geoespacial RAW guardada en: {RUTA_SALIDA}")
    reporte.guardar()
    print(f"Reporte guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()
