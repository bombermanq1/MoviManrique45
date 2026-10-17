"""Carga y validación de los insumos aprobados para el dashboard web."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RUTA_HECHOS = RAIZ / "powerbi" / "geospatial" / "hechos_siniestros.csv"
RUTA_AUXILIAR = RAIZ / "data" / "processed" / "siniestros_comuna3_limpios.csv"
RUTA_IDS = RAIZ / "src" / "geospatial" / "ids_cierre_v1.json"
RUTA_WEB = RAIZ / "data" / "processed" / "geospatial" / "web"
RUTA_COMUNAS = RAIZ / "data" / "raw" / "comunas_medellin.geojson"
RUTA_MANIFIESTO = RAIZ / "data" / "manifest_demo_v1.json"
CONTEOS_ESPERADOS = {"principal_50m": 604, "sensibilidad_borde": 40, "revision_territorial": 4, "resto_manrique": 7684}


def exigir_archivos(rutas: tuple[Path, ...]) -> None:
    """Da un error accionable cuando falten insumos no versionados del demo."""
    faltantes = [str(ruta.relative_to(RAIZ)) for ruta in rutas if not ruta.exists()]
    if faltantes:
        raise FileNotFoundError(
            "Faltan insumos locales del MVP: " + ", ".join(faltantes)
            + f". Revise {RUTA_MANIFIESTO.relative_to(RAIZ)} y ejecute scripts/verificar_insumos_demo.py."
        )


def cargar_hechos() -> pd.DataFrame:
    """Une fecha y coordenadas 1:1 sin modificar las fuentes CSV."""
    exigir_archivos((RUTA_HECHOS, RUTA_AUXILIAR, RUTA_IDS))
    hechos = pd.read_csv(RUTA_HECHOS, dtype={"evento_id": "string", "zona_id": "string"})
    auxiliar = pd.read_csv(RUTA_AUXILIAR, usecols=["objectid", "fecha_siniestro", "latitud", "longitud"], dtype={"objectid": "string"}).rename(columns={"objectid": "evento_id"})
    if hechos["evento_id"].duplicated().any() or auxiliar["evento_id"].duplicated().any():
        raise ValueError("La unión de hechos y coordenadas exige IDs únicos en ambas fuentes.")
    datos = hechos.merge(auxiliar, on="evento_id", how="left", validate="one_to_one")
    if datos[["fecha_siniestro", "latitud", "longitud"]].isna().any().any():
        raise ValueError("La unión 1:1 de fecha y coordenadas produjo valores faltantes.")
    datos["fecha_siniestro"] = pd.to_datetime(datos["fecha_siniestro"], format="%Y-%m-%d", errors="raise")
    if not (datos["fecha_siniestro"].dt.year == datos["anio"]).all():
        raise ValueError("El año de la fecha auxiliar no coincide con el año validado.")
    return datos


def validar_cierre(datos: pd.DataFrame) -> dict[str, int | bool]:
    """Comprueba conteos e IDs congelados antes de mostrar el tablero."""
    conteos = datos["categoria_analisis"].value_counts().to_dict()
    if len(datos) != 8332 or datos["evento_id"].nunique() != 8332:
        raise ValueError("El dashboard exige 8.332 eventos con IDs únicos.")
    if {clave: conteos.get(clave, 0) for clave in CONTEOS_ESPERADOS} != CONTEOS_ESPERADOS:
        raise ValueError("Los conteos de categorías no coinciden con el cierre geoespacial.")
    ids_cierre = json.loads(RUTA_IDS.read_text(encoding="utf-8"))
    for categoria, ids_congelados in ids_cierre.items():
        ids_esperados = {str(valor) for valor in ids_congelados}
        ids_observados = set(datos.loc[datos["categoria_analisis"] == categoria, "evento_id"].astype(str))
        if ids_esperados != ids_observados:
            raise ValueError(
                f"Los IDs congelados de la categoría {categoria!r} no coinciden con el cierre geoespacial."
            )
    return {"filas": len(datos), "ids_unicos": datos["evento_id"].nunique() == len(datos), **CONTEOS_ESPERADOS}


def cargar_geojson(nombre: str) -> dict:
    """Lee geometrías de referencia verificadas, ya exportadas en EPSG:4326."""
    ruta = RUTA_WEB / nombre
    exigir_archivos((ruta,))
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_limite_manrique() -> dict:
    """Devuelve el límite oficial de Manrique en EPSG:4326 para el visor web.

    La función solo lee la capa RAW oficial: no altera geometrías, atributos ni
    archivos fuente. La reproyección se produce en memoria porque GeoJSON web
    usa coordenadas geográficas.
    """
    exigir_archivos((RUTA_COMUNAS,))
    comunas = gpd.read_file(RUTA_COMUNAS)
    columnas_requeridas = {"codigo", "nombre", "geometry"}
    if not columnas_requeridas.issubset(comunas.columns):
        raise ValueError("La capa oficial de comunas no contiene los campos esperados.")
    if comunas.crs is None or comunas.crs.to_epsg() != 9377:
        raise ValueError("El límite oficial de comunas debe estar en EPSG:9377.")

    codigo = comunas["codigo"].astype(str).str.strip().str.zfill(2)
    nombre = comunas["nombre"].astype(str).str.strip().str.casefold()
    manrique = comunas.loc[(codigo == "03") & (nombre == "manrique")].copy()
    if len(manrique) != 1:
        raise ValueError("Se esperaba exactamente un polígono oficial para Comuna 3 - Manrique.")
    if manrique.geometry.isna().any() or manrique.geometry.is_empty.any() or not manrique.geometry.is_valid.all():
        raise ValueError("El polígono oficial de Manrique no supera las validaciones geométricas.")

    return json.loads(manrique.to_crs("EPSG:4326").to_json())
