"""Descarga de siniestros viales desde ArcGIS REST de Medellín.

Esta primera versión conserva los atributos originales publicados por la fuente.
No aplica limpieza, eliminación de nulos ni filtros por corredor vial.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests


URL_CAPA = (
    "https://www.medellin.gov.co/servidormapas/rest/services/"
    "transporte/VM_Accidentes/MapServer/0"
)
TIEMPO_ESPERA_SEGUNDOS = 60

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_SINIESTROS_RAW = RAIZ_PROYECTO / "data" / "raw" / "siniestros_medellin.csv"
RUTA_SINIESTROS_COMUNA3 = (
    RAIZ_PROYECTO / "data" / "processed" / "siniestros_comuna3.csv"
)


def solicitar_json(url: str, parametros: dict[str, Any]) -> dict[str, Any]:
    """Consulta ArcGIS, valida errores HTTP y errores devueltos por el servicio."""
    respuesta = requests.get(url, params=parametros, timeout=TIEMPO_ESPERA_SEGUNDOS)
    respuesta.raise_for_status()

    datos = respuesta.json()
    if "error" in datos:
        detalle = datos["error"]
        raise RuntimeError(
            f"Error de ArcGIS ({detalle.get('code', 'sin código')}): "
            f"{detalle.get('message', detalle)}"
        )
    return datos


def obtener_metadatos_capa(url_capa: str) -> dict[str, Any]:
    """Obtiene el esquema y los límites publicados por la capa oficial."""
    return solicitar_json(url_capa, {"f": "json"})


def descargar_siniestros(url_capa: str, tamano_pagina: int) -> pd.DataFrame:
    """Descarga todas las páginas de atributos y las convierte en un DataFrame."""
    url_consulta = f"{url_capa}/query"
    registros: list[dict[str, Any]] = []
    desplazamiento = 0

    while True:
        parametros = {
            "f": "json",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "resultOffset": desplazamiento,
            "resultRecordCount": tamano_pagina,
            # El orden estable evita que la paginación dependa del orden interno del servicio.
            "orderByFields": "objectid ASC",
        }
        pagina = solicitar_json(url_consulta, parametros)
        entidades = pagina.get("features", [])

        if not entidades:
            break

        registros.extend(entidad.get("attributes", {}) for entidad in entidades)
        print(f"Registros descargados: {len(registros)}")

        if len(entidades) < tamano_pagina:
            break
        desplazamiento += len(entidades)

    return pd.DataFrame(registros)


def nombre_columna(campos: list[str], nombre_real: str) -> str | None:
    """Busca un nombre de campo sin asumir diferencias de mayúsculas/minúsculas."""
    return next((campo for campo in campos if campo.lower() == nombre_real.lower()), None)


def mostrar_resumen(df: pd.DataFrame) -> tuple[str | None, str | None]:
    """Muestra el perfil inicial y retorna los campos reales de año y comuna."""
    campos = df.columns.tolist()
    columna_anio = nombre_columna(campos, "anio")
    columna_num_comuna = nombre_columna(campos, "num_comuna")
    columna_nom_comuna = nombre_columna(campos, "nom_comuna")

    print(f"\nCantidad de registros descargados: {len(df)}")
    print("\nNombres de las columnas:")
    print(campos)

    print("\nAños disponibles:")
    if columna_anio:
        print(sorted(df[columna_anio].dropna().unique().tolist()))
    else:
        print("No se encontró un campo de año en la respuesta de la API.")

    print("\nComunas disponibles:")
    columnas_comuna = [
        columna
        for columna in (columna_num_comuna, columna_nom_comuna)
        if columna is not None
    ]
    if columnas_comuna:
        print(
            df[columnas_comuna]
            .drop_duplicates()
            .sort_values(columnas_comuna, na_position="last")
            .to_string(index=False)
        )
    else:
        print("No se encontraron campos de comuna en la respuesta de la API.")

    print("\nCantidad de valores nulos por columna:")
    print(df.isna().sum().to_string())

    return columna_num_comuna, columna_nom_comuna


def filtrar_comuna_manrique(
    df: pd.DataFrame, columna_num_comuna: str | None, columna_nom_comuna: str | None
) -> pd.DataFrame:
    """Filtra la Comuna 3 usando el valor realmente disponible en la descarga."""
    if columna_nom_comuna:
        mascara_manrique = (
            df[columna_nom_comuna]
            .fillna("")
            .astype(str)
            .str.contains("MANRIQUE", case=False, regex=False)
        )
        if mascara_manrique.any():
            print(
                "\nFiltro aplicado: "
                f"{columna_nom_comuna} contiene 'MANRIQUE' "
                "(valor observado en la API)."
            )
            return df.loc[mascara_manrique].copy()

    if columna_num_comuna:
        mascara_comuna3 = df[columna_num_comuna].fillna("").astype(str).str.strip().eq("3")
        if mascara_comuna3.any():
            print(
                "\nFiltro aplicado: "
                f"{columna_num_comuna} es igual a '3' "
                "(valor observado en la API)."
            )
            return df.loc[mascara_comuna3].copy()

    raise ValueError(
        "No fue posible identificar la Comuna 3 - Manrique con los campos reales "
        "devueltos por la API. Revise la lista de comunas mostrada en consola."
    )


def guardar_csv(df: pd.DataFrame, ruta: Path) -> None:
    """Guarda el DataFrame sin índice y crea el directorio de salida si hace falta."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8-sig")


def main() -> None:
    """Ejecuta la descarga, el perfil inicial y el filtro de Comuna 3 - Manrique."""
    try:
        metadatos = obtener_metadatos_capa(URL_CAPA)
        maximo_api = int(metadatos.get("maxRecordCount", 2000))
        # Se respeta el máximo publicado por la fuente para cada página.
        siniestros = descargar_siniestros(URL_CAPA, tamano_pagina=maximo_api)
    except (requests.RequestException, ValueError, RuntimeError) as error:
        print(f"No fue posible descargar los siniestros: {error}")
        return

    guardar_csv(siniestros, RUTA_SINIESTROS_RAW)
    columna_num_comuna, columna_nom_comuna = mostrar_resumen(siniestros)

    try:
        siniestros_comuna3 = filtrar_comuna_manrique(
            siniestros, columna_num_comuna, columna_nom_comuna
        )
    except ValueError as error:
        print(f"No se generó el archivo filtrado: {error}")
        return

    guardar_csv(siniestros_comuna3, RUTA_SINIESTROS_COMUNA3)
    print(f"\nArchivo original guardado en: {RUTA_SINIESTROS_RAW}")
    print(f"Archivo Comuna 3 - Manrique guardado en: {RUTA_SINIESTROS_COMUNA3}")


if __name__ == "__main__":
    main()
