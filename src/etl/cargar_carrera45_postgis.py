"""Consulta la tabla de Carrera 45; escribir requiere una confirmación explícita.

Este módulo no abre conexiones ni solicita contraseñas al importarse. Por
defecto verifica en modo lectura si existe la tabla esperada. La creación de
una tabla sigue disponible únicamente para una ejecución consciente con
``--permitir-escritura``; no se invoca desde el MVP ni desde las pruebas.
"""

from __future__ import annotations

import argparse
import getpass
from pathlib import Path

import geopandas as gpd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


RAIZ = Path(__file__).resolve().parents[2]
RUTA_EJE = RAIZ / "data" / "processed" / "carrera45_manrique.geojson"


def crear_engine(contrasena: str):
    """Crea una conexión local solo cuando la persona ejecuta el script."""
    url = URL.create(
        "postgresql+psycopg",
        username="postgres",
        password=contrasena,
        host="localhost",
        port=5432,
        database="movimanrique45",
    )
    return create_engine(url)


def tabla_existe(conexion) -> bool:
    """Consulta metadatos sin modificar PostgreSQL."""
    return bool(conexion.execute(text("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'carrera45_segmentos'
        )
    """)).scalar())


def cargar_eje() -> gpd.GeoDataFrame:
    """Valida el archivo local antes de una eventual operación autorizada."""
    eje = gpd.read_file(RUTA_EJE)
    if len(eje) != 26:
        raise ValueError("Se esperaban 26 segmentos en el eje definitivo.")
    if eje.crs is None or eje.crs.to_epsg() != 9377:
        raise ValueError("El eje definitivo debe estar en EPSG:9377.")
    return eje


def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta segura de Carrera 45 en PostgreSQL.")
    parser.add_argument(
        "--permitir-escritura",
        action="store_true",
        help="autoriza explícitamente crear la tabla si falta; el valor predeterminado es solo lectura",
    )
    argumentos = parser.parse_args()
    contrasena = getpass.getpass("Contraseña PostgreSQL: ")
    engine = crear_engine(contrasena)

    try:
        with engine.connect() as conexion:
            existe = tabla_existe(conexion)

        if existe:
            with engine.connect() as conexion:
                total = conexion.execute(text("SELECT COUNT(*) FROM public.carrera45_segmentos")).scalar()
            print(f"La tabla existe y contiene {total} registros. No se modificaron datos.")
            return 0

        if not argumentos.permitir_escritura:
            print("La tabla no existe. Modo solo lectura: no se creó ninguna tabla.")
            return 2

        eje = cargar_eje()
        with engine.begin() as conexion:
            eje.to_postgis(
                name="carrera45_segmentos",
                con=conexion,
                schema="public",
                if_exists="fail",
                index=False,
            )
        print("Tabla creada mediante autorización explícita.")
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
