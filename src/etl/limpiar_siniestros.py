"""Crea una capa validada de siniestros de Comuna 3 sin alterar el CSV original."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_ENTRADA = RAIZ_PROYECTO / "data" / "processed" / "siniestros_comuna3.csv"
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "processed" / "siniestros_comuna3_limpios.csv"
RUTA_REPORTE = RAIZ_PROYECTO / "reports" / "reporte_limpieza_siniestros.txt"


class Reporte:
    """Centraliza mensajes para consola y el reporte persistente."""

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def agregar(self, texto: Any = "") -> None:
        """Imprime y acumula una línea del proceso de validación."""
        contenido = str(texto)
        print(contenido)
        self.lineas.append(contenido)

    def guardar(self) -> None:
        """Crea la carpeta reports si no existe y guarda el reporte de texto."""
        RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
        RUTA_REPORTE.write_text("\n".join(self.lineas) + "\n", encoding="utf-8")


def buscar_columna(df: pd.DataFrame, nombre: str) -> str | None:
    """Retorna el nombre real de una columna sin suponer mayúsculas/minúsculas."""
    return next((columna for columna in df.columns if columna.lower() == nombre.lower()), None)


def limpiar_espacios_texto(df: pd.DataFrame) -> list[str]:
    """Recorta solo espacios externos de valores de texto, sin cambiar categorías."""
    columnas_transformadas: list[str] = []
    for columna in df.select_dtypes(include=["object", "string"]).columns:
        # Se preservan valores no textuales y nulos tal como están.
        df[columna] = df[columna].map(
            lambda valor: valor.strip() if isinstance(valor, str) else valor
        )
        columnas_transformadas.append(columna)
    return columnas_transformadas


def convertir_anio(df: pd.DataFrame) -> tuple[int, str | None]:
    """Valida que anio sea entero y convierte sus valores flotantes a entero."""
    columna = buscar_columna(df, "anio")
    if not columna:
        return 0, None

    anio_numerico = pd.to_numeric(df[columna].copy(), errors="coerce")
    invalidos = anio_numerico.isna() | anio_numerico.ne(anio_numerico.round())
    cantidad_invalidos = int(invalidos.sum())

    if cantidad_invalidos == 0:
        # La conversión se hace solo después de comprobar que no se perderán valores.
        df[columna] = anio_numerico.astype(int)
    return cantidad_invalidos, columna


def validar_y_convertir_fechas(df: pd.DataFrame) -> tuple[int, str | None]:
    """Convierte fechas ISO y cuenta fallos antes de permitir el guardado final."""
    columna = buscar_columna(df, "fecha_siniestro")
    if not columna:
        return 0, None

    fechas = pd.to_datetime(
        df[columna].copy(), format="%Y-%m-%d", errors="coerce"
    )
    invalidas = df[columna].notna() & fechas.isna()
    cantidad_invalidas = int(invalidas.sum())

    if cantidad_invalidas == 0:
        # Solo se reemplaza la columna al confirmar que todos los valores son válidos.
        df[columna] = fechas
    return cantidad_invalidas, columna


def validar_horas(df: pd.DataFrame) -> tuple[int, int, str | None]:
    """Verifica HH:MM:SS sin transformar ni reemplazar el valor original."""
    columna = buscar_columna(df, "hora_siniestro")
    if not columna:
        return 0, 0, None

    horas_texto = df[columna].copy()
    horas_convertidas = pd.to_datetime(horas_texto, format="%H:%M:%S", errors="coerce")
    invalidas = horas_texto.notna() & horas_convertidas.isna()
    return int(invalidas.sum()), int(horas_texto.isna().sum()), columna


def validar_coordenadas(df: pd.DataFrame) -> dict[str, int | str | None]:
    """Registra coordenadas no numéricas o fuera de rango, sin corregirlas."""
    latitud = buscar_columna(df, "latitud")
    longitud = buscar_columna(df, "longitud")
    resultado: dict[str, int | str | None] = {
        "columna_latitud": latitud,
        "columna_longitud": longitud,
        "latitudes_invalidas": 0,
        "longitudes_invalidas": 0,
        "filas_coordenadas_invalidas": 0,
    }
    if not latitud or not longitud:
        return resultado

    latitud_numerica = pd.to_numeric(df[latitud].copy(), errors="coerce")
    longitud_numerica = pd.to_numeric(df[longitud].copy(), errors="coerce")
    latitud_invalida = latitud_numerica.isna() | ~latitud_numerica.between(-90, 90)
    longitud_invalida = longitud_numerica.isna() | ~longitud_numerica.between(-180, 180)

    resultado["latitudes_invalidas"] = int(latitud_invalida.sum())
    resultado["longitudes_invalidas"] = int(longitud_invalida.sum())
    resultado["filas_coordenadas_invalidas"] = int(
        (latitud_invalida | longitud_invalida).sum()
    )
    return resultado


def contar_duplicados_y_nulos(df: pd.DataFrame) -> dict[str, Any]:
    """Calcula diagnósticos posteriores a la validación sin eliminar registros."""
    objectid = buscar_columna(df, "objectid")
    radicado = buscar_columna(df, "radicado")
    return {
        "filas_duplicadas": int(df.duplicated().sum()),
        "objectid_duplicados": int(df[objectid].duplicated().sum()) if objectid else None,
        "radicado_duplicados": int(df[radicado].duplicated().sum()) if radicado else None,
        "nulos_por_columna": df.isna().sum(),
    }


def escribir_reporte(
    reporte: Reporte,
    filas_entrada: int,
    df: pd.DataFrame,
    columnas_texto: list[str],
    anio_invalidos: int,
    columna_anio: str | None,
    fechas_invalidas: int,
    columna_fecha: str | None,
    horas_invalidas: int,
    horas_nulas: int,
    columna_hora: str | None,
    coordenadas: dict[str, int | str | None],
    diagnostico: dict[str, Any],
    se_guardo_salida: bool,
) -> None:
    """Documenta transformaciones y validaciones efectuadas durante la limpieza."""
    reporte.agregar("REPORTE DE LIMPIEZA - SINIESTROS COMUNA 3 - MANRIQUE")
    reporte.agregar(f"Archivo de entrada: {RUTA_ENTRADA}")
    reporte.agregar(f"Archivo de salida: {RUTA_SALIDA}")
    reporte.agregar(f"Registros de entrada: {filas_entrada}")
    reporte.agregar(f"Registros de salida: {len(df) if se_guardo_salida else 0}")
    reporte.agregar(f"Columnas ({len(df.columns)}): {', '.join(df.columns)}")

    reporte.agregar("\nTransformaciones realizadas:")
    reporte.agregar(
        "- Se recortaron exclusivamente espacios iniciales y finales en columnas de texto: "
        + (", ".join(columnas_texto) if columnas_texto else "ninguna")
    )
    if columna_anio:
        reporte.agregar(
            f"- {columna_anio} se convirtió de valor numérico flotante a entero."
        )
    if columna_fecha:
        reporte.agregar(
            f"- {columna_fecha} se convirtió a datetime con formato %Y-%m-%d."
        )
    reporte.agregar("- hora_siniestro y coordenadas no se modificaron.")

    reporte.agregar("\nValidaciones:")
    reporte.agregar(f"Años inválidos para conversión a entero: {anio_invalidos}")
    reporte.agregar(f"Fechas inválidas: {fechas_invalidas}")
    reporte.agregar(f"Horas inválidas: {horas_invalidas}")
    reporte.agregar(f"Horas nulas: {horas_nulas}")
    reporte.agregar(
        f"Latitudes inválidas: {coordenadas['latitudes_invalidas']} | "
        f"Longitudes inválidas: {coordenadas['longitudes_invalidas']} | "
        f"Filas con coordenadas inválidas: {coordenadas['filas_coordenadas_invalidas']}"
    )
    reporte.agregar(
        f"Filas completamente duplicadas: {diagnostico['filas_duplicadas']}"
    )
    reporte.agregar(f"objectid duplicados: {diagnostico['objectid_duplicados']}")
    reporte.agregar(f"radicado duplicados: {diagnostico['radicado_duplicados']}")
    reporte.agregar("\nValores nulos por columna:")
    reporte.agregar(diagnostico["nulos_por_columna"].to_string())

    reporte.agregar("\nRegistros descartados: 0")
    reporte.agregar(
        "Justificación de descartes: no se descartaron registros. Las coordenadas "
        "repetidas se conservan porque distintos siniestros pueden compartir ubicación."
    )
    reporte.agregar(
        "Estado de salida: "
        + ("archivo limpio guardado." if se_guardo_salida else "archivo no guardado por validaciones fallidas.")
    )


def main() -> None:
    """Ejecuta una limpieza mínima y validada, preservando todas las filas válidas."""
    if not RUTA_ENTRADA.exists():
        print(f"No se encontró el archivo de entrada: {RUTA_ENTRADA}")
        return

    try:
        # El CSV de entrada solo se lee; nunca se sobrescribe.
        siniestros = pd.read_csv(RUTA_ENTRADA)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        print(f"No fue posible leer el CSV de entrada: {error}")
        return

    filas_entrada = len(siniestros)
    columnas_texto = limpiar_espacios_texto(siniestros)
    anio_invalidos, columna_anio = convertir_anio(siniestros)
    fechas_invalidas, columna_fecha = validar_y_convertir_fechas(siniestros)
    horas_invalidas, horas_nulas, columna_hora = validar_horas(siniestros)
    coordenadas = validar_coordenadas(siniestros)
    diagnostico = contar_duplicados_y_nulos(siniestros)

    # Año y fecha son las únicas conversiones estructurales. Si fallan, no se guarda
    # una salida parcialmente convertida; el reporte conserva el diagnóstico.
    conversiones_validas = anio_invalidos == 0 and fechas_invalidas == 0
    if conversiones_validas:
        RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
        siniestros.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")

    reporte = Reporte()
    escribir_reporte(
        reporte,
        filas_entrada,
        siniestros,
        columnas_texto,
        anio_invalidos,
        columna_anio,
        fechas_invalidas,
        columna_fecha,
        horas_invalidas,
        horas_nulas,
        columna_hora,
        coordenadas,
        diagnostico,
        conversiones_validas,
    )
    reporte.guardar()
    print(f"\nReporte guardado en: {RUTA_REPORTE}")
    if conversiones_validas:
        print(f"Archivo limpio guardado en: {RUTA_SALIDA}")
    else:
        print("No se generó el archivo limpio: se detectaron conversiones inválidas.")


if __name__ == "__main__":
    main()
