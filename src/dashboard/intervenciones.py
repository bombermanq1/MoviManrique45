"""Construye fichas exploratorias de intervenciones desde insumos validados.

El módulo no modifica fuentes RAW, datasets procesados, geometrías ni IDs del
cierre. Sus salidas son una vista local para el dashboard: cada ficha conserva
los conteos históricos observados de la celda y separa explícitamente las
propuestas candidatas de cualquier decisión de obra.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd

from src.dashboard.datos import RUTA_WEB, cargar_hechos, exigir_archivos, validar_cierre


RAIZ = Path(__file__).resolve().parents[2]
RUTA_ZONAS = RUTA_WEB / "zonas_prioritarias.geojson"
RUTA_EJE = RUTA_WEB / "carrera45.geojson"
RUTA_SALIDA = RAIZ / "web" / "data" / "intervenciones.json"
ESTADO_INICIAL = "Pendiente de inspección"

# Catálogo de referencia. Ninguna medida se asigna ni se aprueba automáticamente:
# la ficha solo invita a evaluarla durante una inspección de campo y el diseño técnico.
CATALOGO_INTERVENCIONES: tuple[dict[str, Any], ...] = (
    {
        "id": "pasos_peatonales_seguros",
        "nombre": "Pasos peatonales seguros",
        "descripcion": "Revisar la ubicación, visibilidad, demarcación y continuidad de los cruces peatonales.",
        "problema_atendido": "Conflictos posibles al cruzar y condiciones de quienes caminan.",
        "beneficio_hipotesis": "Podría hacer más claro y seguro el cruce si la revisión de campo lo confirma.",
        "condiciones_necesarias": "Aforo peatonal, revisión de velocidades, distancias de visibilidad, diseño y autorización.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Secretaría de Movilidad de Medellín y la entidad competente según el alcance del diseño.",
    },
    {
        "id": "reductores_velocidad",
        "nombre": "Reductores de velocidad",
        "descripcion": "Evaluar medidas físicas para moderar la velocidad, compatibles con la vía y su operación.",
        "problema_atendido": "Velocidades que necesitan medirse antes de tomar una decisión.",
        "beneficio_hipotesis": "Podrían ayudar a moderar la velocidad si los estudios técnicos y la autoridad lo aprueban.",
        "condiciones_necesarias": "Medición de velocidad, análisis de transporte público, drenaje, diseño y autorización.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Secretaría de Movilidad de Medellín con las dependencias técnicas competentes.",
    },
    {
        "id": "senalizacion",
        "nombre": "Señalización horizontal y vertical",
        "descripcion": "Revisar demarcación, señales, legibilidad y coherencia con la regulación vigente.",
        "problema_atendido": "Información vial o peatonal que debe verificarse directamente en el lugar.",
        "beneficio_hipotesis": "Podría hacer más claras las maniobras y los cruces si se encuentran necesidades reales.",
        "condiciones_necesarias": "Inventario de señalización, inspección nocturna cuando corresponda, diseño y autorización.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Secretaría de Movilidad de Medellín y responsables de la infraestructura vial.",
    },
    {
        "id": "accesibilidad_universal",
        "nombre": "Mejoramiento de accesibilidad universal",
        "descripcion": "Revisar continuidad, ancho útil, obstáculos y condiciones para caminar.",
        "problema_atendido": "Barreras de accesibilidad que los registros históricos no permiten confirmar.",
        "beneficio_hipotesis": "Podría facilitar recorridos seguros y continuos para distintas personas usuarias.",
        "condiciones_necesarias": "Auditoría de accesibilidad, levantamiento físico, participación y diseño autorizado.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Dependencias municipales competentes en movilidad, espacio público y accesibilidad.",
    },
    {
        "id": "rampas_cruces",
        "nombre": "Rampas y adecuación de cruces",
        "descripcion": "Evaluar rebajes, pendientes, alineación y continuidad de los cruces accesibles.",
        "problema_atendido": "Posibles interrupciones en el paso que requieren medición en campo.",
        "beneficio_hipotesis": "Podría reducir barreras de desplazamiento si el diseño cumple los requisitos técnicos.",
        "condiciones_necesarias": "Medición de pendientes, drenaje, accesibilidad, planos y autorización.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Dependencias municipales competentes en espacio público y movilidad.",
    },
    {
        "id": "control_velocidad",
        "nombre": "Medidas de control de velocidad",
        "descripcion": "Revisar la gestión, el control y la comunicación de velocidades con evidencia de la operación real.",
        "problema_atendido": "Velocidades y comportamientos que los datos históricos por sí solos no muestran.",
        "beneficio_hipotesis": "Podría apoyar el cumplimiento de velocidades adecuadas si la operación de la vía lo sustenta.",
        "condiciones_necesarias": "Aforos, mediciones de velocidad, revisión operativa y definición institucional.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Secretaría de Movilidad de Medellín.",
    },
    {
        "id": "proteccion_peatones_transporte",
        "nombre": "Protección de peatones cerca de transporte",
        "descripcion": "Revisar espera, cruce y visibilidad en puntos con transporte o ascenso y descenso, si existen.",
        "problema_atendido": "Conflictos peatonales que requieren confirmar la presencia y operación del transporte.",
        "beneficio_hipotesis": "Podría mejorar las condiciones de espera y cruce cuando el contexto de campo lo justifique.",
        "condiciones_necesarias": "Inventario de paradas, aforos peatonales, coordinación operativa y diseño autorizado.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Secretaría de Movilidad de Medellín y operadores o entidades competentes.",
    },
    {
        "id": "visibilidad_espacio_peatonal",
        "nombre": "Mejoramiento de visibilidad y espacio peatonal",
        "descripcion": "Revisar iluminación, obstáculos visuales y condiciones del espacio para caminar.",
        "problema_atendido": "Condiciones físicas que requieren una visita diurna y, cuando aplique, nocturna.",
        "beneficio_hipotesis": "Podría ayudar a entender mejor el entorno si se confirman necesidades.",
        "condiciones_necesarias": "Inspección de campo, inventario físico, coordinación institucional y diseño autorizado.",
        "requiere_inspeccion_campo": True,
        "entidad_evaluadora": "Dependencias municipales competentes en movilidad, espacio público e iluminación.",
    },
)

CONDICIONES_POR_VERIFICAR = (
    "Velocidades que se observan en la vía y forma de circulación.",
    "Visibilidad, iluminación y estado de las señales.",
    "Estado de andenes y cruces, pendientes, continuidad y obstáculos.",
    "Paso de peatones, operación del transporte y maniobras que puedan generar conflicto.",
)

LIMITACIONES_FICHA = (
    "Los registros históricos muestran concentraciones, no exposición, tasa de riesgo ni causalidad.",
    "La zona identificada ayuda a organizar una visita de campo; no reemplaza una auditoría de seguridad vial.",
    "Que una celda toque el eje aporta contexto espacial, pero no permite atribuir el siniestro a la vía.",
    "Aún no hay cantidades de obra ni precios unitarios verificables para estimar costos por zona.",
)


def _conteos_ordenados(serie: pd.Series) -> list[dict[str, int | str]]:
    """Convierte frecuencias observadas a una estructura JSON estable."""
    conteos = Counter(str(valor) for valor in serie.dropna())
    return [
        {"valor": valor, "cantidad": cantidad}
        for valor, cantidad in sorted(conteos.items(), key=lambda item: (-item[1], item[0]))
    ]


def _top_barrios(datos: pd.DataFrame) -> list[dict[str, int | str]]:
    """Entrega barrios nominales observados, sin inferir límites territoriales."""
    return _conteos_ordenados(datos["barrio"])[:5]


def _segmentos_intersectados(zona: Any, eje: gpd.GeoDataFrame) -> list[int | str]:
    """Devuelve únicamente objectid de segmentos que intersectan la celda."""
    coincidencias = eje.loc[eje.geometry.intersects(zona), "objectid"]
    return sorted(
        [int(valor) if pd.notna(valor) and float(valor).is_integer() else str(valor) for valor in coincidencias],
        key=lambda valor: (isinstance(valor, str), valor),
    )


def _ficha_zona(
    fila: pd.Series,
    eventos: pd.DataFrame,
    eje: gpd.GeoDataFrame,
    orden: int,
) -> dict[str, Any]:
    """Crea la ficha de una zona con métricas calculadas, no inventadas."""
    zona_id = str(fila["zona_id"])
    historicos = eventos.loc[eventos["zona_id"].astype("string") == zona_id].copy()
    cantidad_capa = int(fila["cantidad"])
    if len(historicos) != cantidad_capa:
        raise ValueError(
            f"La zona {zona_id} declara {cantidad_capa} registros, pero la vista de eventos contiene {len(historicos)}."
        )

    categoria = _conteos_ordenados(historicos["categoria_analisis"])
    principal = int(historicos["categoria_analisis"].eq("principal_50m").sum())
    punto = fila.geometry.representative_point()
    min_x, min_y, max_x, max_y = fila.geometry.bounds
    segmentos = _segmentos_intersectados(fila.geometry, eje)
    periodo = {
        "inicio": int(historicos["anio"].min()),
        "fin": int(historicos["anio"].max()),
    }
    if segmentos:
        contexto_segmento = (
            "Esta zona toca uno o más tramos del eje de Carrera 45. "
            "Esa coincidencia ayuda a leer el mapa, pero no demuestra una causa."
        )
    else:
        contexto_segmento = (
            "Esta zona no toca de forma geométrica el eje de Carrera 45 exportado. "
            "La ficha conserva sus registros históricos sin asignarlos forzosamente a la vía."
        )

    return {
        "zona_id": zona_id,
        "estado_evaluacion": ESTADO_INICIAL,
        "ubicacion": {
            "referencia": "Zona identificada a partir de registros históricos en la Comuna 3 - Manrique",
            "centroide_representativo_wgs84": {"longitud": round(float(punto.x), 6), "latitud": round(float(punto.y), 6)},
            "bounds_wgs84": [round(float(valor), 6) for valor in (min_x, min_y, max_x, max_y)],
        },
        "evidencia_geoespacial": {
            "cantidad_registros_celda": cantidad_capa,
            "segmentos_eje_intersectados_objectid": segmentos,
            "mensaje_segmento": contexto_segmento,
        },
        "diagnostico_historico": {
            "registros_historicos": len(historicos),
            "periodo": periodo,
            "corredor_estricto_50m": principal,
            "por_categoria_analisis": categoria,
            "por_gravedad": _conteos_ordenados(historicos["gravedad_siniestro"]),
            "por_tipo": _conteos_ordenados(historicos["clase_siniestro"]),
            "barrios_nominales_observados": _top_barrios(historicos),
        },
        "comparacion_exploratoria": {
            "orden_por_registros_historicos": orden,
            "criterio": "Número histórico de registros por zona, ordenado de mayor a menor. En los empates se usa el identificador de zona.",
            "aclaracion": "No es una puntuación de riesgo ni una prioridad oficial de intervención.",
        },
        "condiciones_por_verificar": list(CONDICIONES_POR_VERIFICAR),
        "intervenciones_candidatas": [medida["id"] for medida in CATALOGO_INTERVENCIONES],
        "justificacion": (
            f"En esta zona se registraron {len(historicos)} siniestros entre {periodo['inicio']} y {periodo['fin']}. "
            "Es un punto de partida para la revisión técnica y de campo, no una decisión automática de obra."
        ),
        "costos_preliminares": {
            "estado": "Pendiente de estudio técnico y presupuesto",
            "nota": "Aún no se estima un costo por zona: faltan cantidades de obra y precios unitarios verificables.",
        },
        "limitaciones": list(LIMITACIONES_FICHA),
    }


def construir_payload_intervenciones() -> dict[str, Any]:
    """Calcula las 12 fichas a partir de la vista web y las capas ya validadas."""
    exigir_archivos((RUTA_ZONAS, RUTA_EJE))
    eventos = cargar_hechos()
    validar_cierre(eventos)
    zonas = gpd.read_file(RUTA_ZONAS)
    eje = gpd.read_file(RUTA_EJE)

    requeridas_zonas = {"zona_id", "cantidad", "prioritaria", "geometry"}
    requeridas_eje = {"objectid", "geometry"}
    if not requeridas_zonas.issubset(zonas.columns) or not requeridas_eje.issubset(eje.columns):
        raise ValueError("Las capas web no contienen los campos esperados para intervenciones.")
    if zonas.crs is None or zonas.crs.to_epsg() != 4326 or eje.crs is None or eje.crs.to_epsg() != 4326:
        raise ValueError("Las capas web para el navegador deben estar en EPSG:4326.")
    if len(zonas) != 12 or not zonas["prioritaria"].astype(bool).all() or zonas["zona_id"].duplicated().any():
        raise ValueError("Se requieren exactamente 12 zonas prioritarias reales y con identificadores únicos.")
    if zonas.geometry.isna().any() or zonas.geometry.is_empty.any() or not zonas.geometry.is_valid.all():
        raise ValueError("Las geometrías de zonas prioritarias no superan la validación.")
    if eje.geometry.isna().any() or eje.geometry.is_empty.any() or not eje.geometry.is_valid.all():
        raise ValueError("Las geometrías del eje no superan la validación.")

    ordenadas = zonas.assign(zona_id=zonas["zona_id"].astype(str)).sort_values(
        ["cantidad", "zona_id"], ascending=[False, True]
    )
    orden_por_id = {zona_id: indice for indice, zona_id in enumerate(ordenadas["zona_id"], start=1)}
    fichas = [
        _ficha_zona(fila, eventos, eje, orden_por_id[str(fila["zona_id"])])
        for _, fila in zonas.assign(zona_id=zonas["zona_id"].astype(str)).sort_values("zona_id").iterrows()
    ]

    return {
        "metadatos": {
            "version": "intervenciones_v1",
            "zonas_exploratorias": len(fichas),
            "eventos_validados": len(eventos),
            "estado_inicial": ESTADO_INICIAL,
            "criterio_comparacion": "Número histórico de registros por zona, ordenado de mayor a menor.",
        },
        "catalogo_intervenciones": list(CATALOGO_INTERVENCIONES),
        "zonas": fichas,
        "limitaciones_modulo": list(LIMITACIONES_FICHA),
    }


def exportar_intervenciones(ruta_salida: Path = RUTA_SALIDA) -> Path:
    """Escribe la vista derivada del módulo sin tocar insumos geoespaciales."""
    payload = construir_payload_intervenciones()
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return ruta_salida


def main() -> None:
    ruta = exportar_intervenciones()
    print(f"Intervenciones exportadas: {ruta}")


if __name__ == "__main__":
    main()
