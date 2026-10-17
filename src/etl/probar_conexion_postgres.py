"""Prueba manual de conectividad PostgreSQL sin efectos al importar el módulo."""

from __future__ import annotations

import getpass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def main() -> int:
    contrasena = getpass.getpass("Contraseña PostgreSQL: ")
    url = URL.create(
        "postgresql+psycopg",
        username="postgres",
        password=contrasena,
        host="localhost",
        port=5432,
        database="movimanrique45",
    )
    engine = create_engine(url)
    try:
        with engine.connect() as conexion:
            resultado = conexion.execute(
                text("SELECT current_database(), PostGIS_Version()")
            ).fetchone()
        print("Conexion exitosa")
        print("Base de datos:", resultado[0])
        print("PostGIS:", resultado[1])
        return 0
    except Exception as error:
        print("Error de conexion:", error)
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
