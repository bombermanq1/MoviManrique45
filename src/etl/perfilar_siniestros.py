"""Perfilamiento de solo lectura para siniestros de la Comuna 3 - Manrique."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_ENTRADA = RAIZ_PROYECTO / "data" / "processed" / "siniestros_comuna3.csv"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "perfilamiento_siniestros_comuna3.txt"


class Reporte:
    """Acumula el contenido para consola y para el archivo de reporte."""

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def agregar(self, texto: object = "") -> None:
        """Muestra y conserva una sección del análisis."""
        contenido = str(texto)
        print(contenido)
        self.lineas.append(contenido)

    def guardar(self, ruta: Path) -> None:
        """Crea la carpeta de reportes cuando sea necesaria y escribe el resultado."""
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text("\n".join(self.lineas) + "\n", encoding="utf-8")


def obtener_columna(df: pd.DataFrame, nombre: str) -> str | None:
    """Busca un campo real sin presuponer mayúsculas o minúsculas."""
    return next((columna for columna in df.columns if columna.lower() == nombre.lower()), None)


def analizar_dimension_y_tipos(df: pd.DataFrame, reporte: Reporte) -> None:
    """Describe el tamaño del archivo y los tipos inferidos al leer el CSV."""
    reporte.agregar("\n=== 1. DIMENSIONES ===")
    reporte.agregar(f"Cantidad total de filas: {len(df)}")
    reporte.agregar(f"Cantidad total de columnas: {len(df.columns)}")
    reporte.agregar("\n=== 2. TIPOS DE DATOS ===")
    reporte.agregar(df.dtypes.to_string())


def analizar_nulos(df: pd.DataFrame, reporte: Reporte) -> None:
    """Calcula cantidad y porcentaje de nulos sin alterar el DataFrame."""
    cantidad = df.isna().sum()
    porcentaje = (cantidad / len(df) * 100) if len(df) else cantidad.astype(float)
    resumen = pd.DataFrame(
        {"cantidad_nulos": cantidad, "porcentaje_nulos": porcentaje.round(2)}
    )
    reporte.agregar("\n=== 3. VALORES NULOS ===")
    reporte.agregar(resumen.to_string())


def analizar_duplicados(df: pd.DataFrame, reporte: Reporte) -> None:
    """Cuenta duplicados como diagnóstico; no elimina ninguna fila."""
    reporte.agregar("\n=== 4. DUPLICADOS ===")
    reporte.agregar(f"Filas completamente duplicadas: {int(df.duplicated().sum())}")

    for nombre in ("objectid", "radicado"):
        columna = obtener_columna(df, nombre)
        if columna:
            reporte.agregar(
                f"Valores duplicados en {columna}: {int(df[columna].duplicated().sum())}"
            )
        else:
            reporte.agregar(f"No existe la columna {nombre} en el archivo.")


def analizar_valores_unicos(df: pd.DataFrame, reporte: Reporte) -> None:
    """Muestra frecuencia de las variables categóricas y temporales solicitadas."""
    reporte.agregar("\n=== 5. VALORES ÚNICOS Y CANTIDADES ===")
    for nombre in (
        "clase_siniestro",
        "gravedad_siniestro",
        "anio",
        "dia",
        "mes",
        "nom_comuna",
    ):
        columna = obtener_columna(df, nombre)
        if columna:
            reporte.agregar(f"\n{columna}:")
            # dropna=False incluye los valores nulos como una categoría visible.
            reporte.agregar(df[columna].value_counts(dropna=False).to_string())
        else:
            reporte.agregar(f"\nNo existe la columna {nombre} en el archivo.")


def analizar_barrios(df: pd.DataFrame, reporte: Reporte) -> None:
    """Revisa diversidad, ausencia y frecuencia de barrios sin hacer limpieza."""
    columna = obtener_columna(df, "barrio")
    reporte.agregar("\n=== 6. ANÁLISIS DE BARRIO ===")
    if not columna:
        reporte.agregar("No existe la columna barrio en el archivo.")
        return

    reporte.agregar(f"Cantidad de barrios diferentes: {df[columna].nunique(dropna=True)}")
    reporte.agregar(f"Valores nulos en barrio: {int(df[columna].isna().sum())}")
    reporte.agregar("\n20 barrios con más registros:")
    reporte.agregar(df[columna].value_counts(dropna=False).head(20).to_string())


def analizar_coordenadas(df: pd.DataFrame, reporte: Reporte) -> None:
    """Evalúa rangos y posibles problemas de coordenadas usando copias temporales."""
    latitud = obtener_columna(df, "latitud")
    longitud = obtener_columna(df, "longitud")
    reporte.agregar("\n=== 7. ANÁLISIS DE COORDENADAS ===")
    if not latitud or not longitud:
        reporte.agregar("No se encontraron ambas columnas: latitud y longitud.")
        return

    # La conversión se realiza sobre series nuevas: los valores originales no se cambian.
    latitud_numerica = pd.to_numeric(df[latitud].copy(), errors="coerce")
    longitud_numerica = pd.to_numeric(df[longitud].copy(), errors="coerce")
    coordenadas_nulas = (df[latitud].isna() | df[longitud].isna()).sum()

    reporte.agregar(f"Latitud mínima: {latitud_numerica.min()}")
    reporte.agregar(f"Latitud máxima: {latitud_numerica.max()}")
    reporte.agregar(f"Longitud mínima: {longitud_numerica.min()}")
    reporte.agregar(f"Longitud máxima: {longitud_numerica.max()}")
    reporte.agregar(f"Latitudes nulas: {int(df[latitud].isna().sum())}")
    reporte.agregar(f"Longitudes nulas: {int(df[longitud].isna().sum())}")
    reporte.agregar(f"Filas con al menos una coordenada nula: {int(coordenadas_nulas)}")
    reporte.agregar(f"Latitudes iguales a 0: {int(latitud_numerica.eq(0).sum())}")
    reporte.agregar(f"Longitudes iguales a 0: {int(longitud_numerica.eq(0).sum())}")
    reporte.agregar(
        "Pares latitud/longitud duplicados: "
        f"{int(df[[latitud, longitud]].duplicated().sum())}"
    )


def analizar_fechas(df: pd.DataFrame, reporte: Reporte) -> None:
    """Prueba la conversión de fecha en una copia, sin reemplazar la columna original."""
    columna = obtener_columna(df, "fecha_siniestro")
    reporte.agregar("\n=== 8. ANÁLISIS DE fecha_siniestro ===")
    if not columna:
        reporte.agregar("No existe la columna fecha_siniestro en el archivo.")
        return

    fechas_convertidas = pd.to_datetime(df[columna].copy(), errors="coerce", dayfirst=True)
    no_convertidas = df[columna].notna() & fechas_convertidas.isna()
    reporte.agregar(f"Valores no convertibles a datetime: {int(no_convertidas.sum())}")
    reporte.agregar(f"Fecha mínima: {fechas_convertidas.min()}")
    reporte.agregar(f"Fecha máxima: {fechas_convertidas.max()}")


def analizar_horas(df: pd.DataFrame, reporte: Reporte) -> None:
    """Muestra ejemplos del formato de hora sin realizar una transformación."""
    columna = obtener_columna(df, "hora_siniestro")
    reporte.agregar("\n=== 9. ANÁLISIS DE hora_siniestro ===")
    if not columna:
        reporte.agregar("No existe la columna hora_siniestro en el archivo.")
        return

    # Se seleccionan únicamente valores presentes sin eliminar ni modificar filas.
    valores_presentes = df.loc[df[columna].notna(), columna]
    ejemplos = valores_presentes.astype(str).unique()[:10]
    reporte.agregar("Ejemplos del formato encontrado:")
    reporte.agregar(examples_to_text(ejemplos))
    reporte.agregar(f"Valores nulos en hora_siniestro: {int(df[columna].isna().sum())}")


def examples_to_text(valores: object) -> str:
    """Presenta ejemplos en una línea sin cambiar su contenido original."""
    return ", ".join(map(str, valores)) if len(valores) else "Sin ejemplos no nulos."


def mostrar_ejemplos(df: pd.DataFrame, reporte: Reporte) -> None:
    """Muestra diez ejemplos de los campos solicitados, tal como se leen del CSV."""
    reporte.agregar("\n=== 10. EJEMPLOS DE VALORES ===")
    for nombre in ("direccion", "barrio", "latitud", "longitud"):
        columna = obtener_columna(df, nombre)
        if columna:
            reporte.agregar(f"\n10 ejemplos de {columna}:")
            reporte.agregar(df[columna].head(10).to_string(index=False))
        else:
            reporte.agregar(f"\nNo existe la columna {nombre} en el archivo.")


def main() -> None:
    """Lee el CSV y genera un diagnóstico que no modifica el archivo de entrada."""
    if not RUTA_ENTRADA.exists():
        print(f"No se encontró el archivo de entrada: {RUTA_ENTRADA}")
        return

    try:
        # Solo se lee el archivo; no se sobrescribe ni se crea un dataset limpio.
        siniestros = pd.read_csv(RUTA_ENTRADA)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        print(f"No fue posible leer el CSV de siniestros: {error}")
        return

    reporte = Reporte()
    reporte.agregar("PERFILAMIENTO DE SINIESTROS - COMUNA 3 - MANRIQUE")
    reporte.agregar(f"Archivo analizado: {RUTA_ENTRADA}")
    analizar_dimension_y_tipos(siniestros, reporte)
    analizar_nulos(siniestros, reporte)
    analizar_duplicados(siniestros, reporte)
    analizar_valores_unicos(siniestros, reporte)
    analizar_barrios(siniestros, reporte)
    analizar_coordenadas(siniestros, reporte)
    analizar_fechas(siniestros, reporte)
    analizar_horas(siniestros, reporte)
    mostrar_ejemplos(siniestros, reporte)
    reporte.guardar(RUTA_REPORTE)
    print(f"\nReporte guardado en: {RUTA_REPORTE}")


if __name__ == "__main__":
    main()
