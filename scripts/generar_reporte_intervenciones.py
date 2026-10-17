"""Genera un reporte reproducible del módulo de intervenciones exploratorias."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.dashboard.intervenciones import construir_payload_intervenciones


SALIDA = RAIZ / "reports" / "modulo_intervenciones_v1.md"


def main() -> None:
    payload = construir_payload_intervenciones()
    lineas = [
        "# Módulo de intervenciones v1",
        "",
        "## Alcance verificado",
        "",
        f"- Zonas exploratorias reales disponibles: **{payload['metadatos']['zonas_exploratorias']}**.",
        f"- Eventos validados conservados: **{payload['metadatos']['eventos_validados']:,}**.".replace(",", "."),
        f"- Estado inicial de las fichas: **{payload['metadatos']['estado_inicial']}**.",
        "- El orden comparativo es descriptivo y usa solo el conteo histórico por celda.",
        "- El catálogo contiene ocho medidas candidatas para evaluación, no intervenciones aprobadas.",
        "",
        "## Fichas generadas desde datos reales",
        "",
        "| Orden | Zona | Registros históricos | Corredor estricto | Segmentos del eje intersectados | Estado |",
        "|---:|---|---:|---:|---|---|",
    ]
    zonas = sorted(
        payload["zonas"],
        key=lambda ficha: ficha["comparacion_exploratoria"]["orden_por_registros_historicos"],
    )
    for ficha in zonas:
        segmentos = ficha["evidencia_geoespacial"]["segmentos_eje_intersectados_objectid"]
        texto_segmentos = ", ".join(str(valor) for valor in segmentos) if segmentos else "Sin intersección"
        lineas.append(
            "| {orden} | {zona} | {historicos} | {principal} | {segmentos} | {estado} |".format(
                orden=ficha["comparacion_exploratoria"]["orden_por_registros_historicos"],
                zona=ficha["zona_id"],
                historicos=ficha["diagnostico_historico"]["registros_historicos"],
                principal=ficha["diagnostico_historico"]["corredor_estricto_50m"],
                segmentos=texto_segmentos,
                estado=ficha["estado_evaluacion"],
            )
        )
    lineas += [
        "",
        "## Límites de uso",
        "",
        *[f"- {limite}" for limite in payload["limitaciones_modulo"]],
        "",
        "Los costos por zona permanecen como **Pendiente de estudio técnico y presupuesto**. "
        "Los siniestros históricos no sustituyen inspección de campo, aforos, diseño ni autorización institucional.",
    ]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Reporte generado: {SALIDA}")


if __name__ == "__main__":
    main()
