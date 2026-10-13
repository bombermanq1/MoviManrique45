
import getpass
import geopandas as gpd
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ruta = Path("data/processed/carrera45_manrique.geojson")

gdf = gpd.read_file(ruta)

print("Segmentos encontrados:", len(gdf))
print("Sistema de coordenadas:", gdf.crs)

if len(gdf) != 26:
    raise ValueError("Se esperaban 26 segmentos")

if gdf.crs.to_epsg() != 9377:
    raise ValueError("El CRS debe ser EPSG:9377")

contrasena = getpass.getpass("Contraseña PostgreSQL: ")

url = URL.create(
    "postgresql+psycopg",
    username="postgres",
    password=contrasena,
    host="localhost",
    port=5432,
    database="movimanrique45"
)

engine = create_engine(url)

try:
    with engine.begin() as conexion:
        existe = conexion.execute(text("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'carrera45_segmentos'
            )
        """)).scalar()

        if existe:
            print("La tabla ya existe. No se modificaron datos.")
        else:
            gdf.to_postgis(
                name="carrera45_segmentos",
                con=conexion,
                schema="public",
                if_exists="fail",
                index=False
            )

            print("Segmentos importados correctamente")

        total = conexion.execute(text("""
            SELECT COUNT(*)
            FROM public.carrera45_segmentos
        """)).scalar()

        print("Registros en PostgreSQL:", total)

finally:
    engine.dispose()
