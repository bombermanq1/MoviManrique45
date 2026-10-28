"""Validación estática de los recursos manuales de Power BI.

Lee fuentes locales y escribe únicamente los dos reportes de esta carpeta.
No abre Power BI Desktop, no cambia RAW/procesados ni usa PostgreSQL.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import geopandas as gpd


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
PQ = OUT / "powerquery"
DAX = OUT / "dax" / "medidas_modelo.dax"

EXPECTED_M = [
    "00_parametro_pRaiz.m.template",
    "01_fxRutaProyecto.m",
    "02_fxCsv.m",
    "03_fxBool.m",
    "04_fxControlTabla.m",
    "10_StgHechos.m",
    "11_StgFechaCoordenadas.m",
    "12_StgConFecha.m",
    "20_DimTerritorioNominal.m",
    "21_DimFecha.m",
    "22_DimClasificacion.m",
    "23_DimSegmento.m",
    "24_DimZona.m",
    "25_DimGravedad.m",
    "26_DimTipo.m",
    "27_DimTerritorioGeometrico.m",
    "28_DimIdsCongelados.m",
    "29_RevisionFragmentos.m",
    "30_FactSiniestros.m",
    "40_ValidacionCierre.m",
    "41_ControlCierreEstricto.m",
]

EXPECTED_MEASURES = [
    "Registros",
    "Registros corredor",
    "Registros sensibilidad borde",
    "Registros revisión territorial",
    "Registros resto Manrique",
    "Comuna 3 comparable",
    "Corredor comparable",
    "Porcentaje corredor sobre Comuna 3",
    "Mediana distancia corredor m",
    "Registros sin zona",
    "Registros con coordenada validada",
    "Zonas prioritarias de la versión",
    "Zonas prioritarias con registros en selección",
    "Fragmentos conservados de la versión",
    "Registros mismo periodo anterior",
    "Cambio absoluto anual",
    "Cambio porcentual anual",
    "Corredor mismo periodo anterior",
    "Cambio porcentual corredor",
    "Integridad IDs principal",
    "Conteo IDs congelados principal",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status(
    checks: list[dict[str, object]],
    name: str,
    passed: bool,
    detail: str,
    blocked: bool = False,
) -> None:
    checks.append(
        {
            "control": name,
            "estado": "BLOQUEADO" if blocked else "OK" if passed else "ERROR",
            "detalle": detail,
        }
    )


def same_ids(facts: pd.DataFrame, frozen: dict[str, list[int]], category: str) -> bool:
    actual = set(facts.loc[facts["categoria_analisis"].eq(category), "evento_id"].astype(int))
    return actual == {int(value) for value in frozen[category]}


def parentheses_balanced(dax: str) -> bool:

    stripped = re.sub(r"//.*", "", dax)
    depth = 0
    for char in stripped:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def m_delimiters_balanced(source: str) -> bool:
    """Comprobación léxica conservadora; no sustituye el motor de M."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    stack: list[str] = []
    index = 0
    in_string = False
    in_line_comment = False
    in_block_comment = False
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if in_line_comment:
            if char in "\r\n":
                in_line_comment = False
        elif in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
                index += 1
        elif in_string:
            if char == '"' and nxt == '"':
                index += 1
            elif char == '"':
                in_string = False
        elif char == "/" and nxt == "/":
            in_line_comment = True
            index += 1
        elif char == "/" and nxt == "*":
            in_block_comment = True
            index += 1
        elif char == '"':
            in_string = True
        elif char in pairs:
            stack.append(pairs[char])
        elif char in closing:
            if not stack or stack.pop() != char:
                return False
        index += 1
    return not (stack or in_string or in_block_comment)


def main() -> int:
    checks: list[dict[str, object]] = []
    protected = [
        ROOT / "powerbi/geospatial/hechos_siniestros.csv",
        ROOT / "powerbi/geospatial/categorias_analisis.csv",
        ROOT / "powerbi/geospatial/segmentos.csv",
        ROOT / "powerbi/geospatial/zonas.csv",
        ROOT / "powerbi/geospatial/fragmentos_revision.csv",
        ROOT / "data/processed/siniestros_comuna3_limpios.csv",
        ROOT / "data/processed/geospatial/carrera45_auditoria.gpkg",
        ROOT / "src/geospatial/ids_cierre_v1.json",
    ]
    before = {str(path.relative_to(ROOT)): sha256(path) for path in protected}

    facts = pd.read_csv(ROOT / "powerbi/geospatial/hechos_siniestros.csv")
    clean = pd.read_csv(ROOT / "data/processed/siniestros_comuna3_limpios.csv")
    zones = pd.read_csv(ROOT / "powerbi/geospatial/zonas.csv")
    segments = pd.read_csv(ROOT / "powerbi/geospatial/segmentos.csv")
    fragments = pd.read_csv(ROOT / "powerbi/geospatial/fragmentos_revision.csv")
    parts_gdf = gpd.read_file(
        ROOT / "data/processed/geospatial/carrera45_auditoria.gpkg",
        layer="partes",
    )
    frozen = json.loads((ROOT / "src/geospatial/ids_cierre_v1.json").read_text(encoding="utf-8"))

    counts = facts["categoria_analisis"].value_counts().to_dict()
    status(checks, "Hechos: filas e IDs únicos", len(facts) == 8332 and facts["evento_id"].is_unique,
           f"filas={len(facts)}, IDs únicos={facts['evento_id'].nunique()}")
    status(checks, "Clasificación excluyente", counts == {
        "resto_manrique": 7684,
        "principal_50m": 604,
        "sensibilidad_borde": 40,
        "revision_territorial": 4,
    }, f"conteos={counts}")
    for category, expected in (("principal_50m", 604), ("sensibilidad_borde", 40), ("revision_territorial", 4)):
        status(checks, f"IDs congelados exactos: {category}",
               same_ids(facts, frozen, category) and len(frozen[category]) == expected,
               f"esperados={expected}, observados={int(counts.get(category, 0))}")

    matching_ids = set(facts["evento_id"].astype(int)) == set(clean["objectid"].astype(int))
    joined = facts.merge(
        clean[["objectid", "fecha_siniestro", "latitud", "longitud"]],
        left_on="evento_id", right_on="objectid", how="left", validate="one_to_one"
    )
    dates = pd.to_datetime(joined["fecha_siniestro"], format="%Y-%m-%d", errors="coerce")
    valid_periods = bool((dates.dt.year.eq(joined["anio"]) & dates.dt.month.eq(joined["mes_numero"])).all())
    valid_coords = bool(joined["latitud"].between(-90, 90).all() and joined["longitud"].between(-180, 180).all())
    status(checks, "Unión auxiliar 1:1", matching_ids and joined["fecha_siniestro"].notna().all(),
           f"hechos={len(facts)}, auxiliar={len(clean)}, fechas sin coincidencia={int(joined['fecha_siniestro'].isna().sum())}")
    status(checks, "Fecha y coordenadas auxiliares", dates.notna().all() and valid_periods and valid_coords,
           f"fechas inválidas={int(dates.isna().sum())}, periodos coherentes={valid_periods}, coordenadas en rango={valid_coords}")

    status(checks, "Segmentos", len(segments) == 26 and segments["segmento_cercano_id"].is_unique,
           f"filas={len(segments)}, IDs únicos={segments['segmento_cercano_id'].nunique()}")
    status(
        checks,
        "Partes geométricas",
        len(parts_gdf) == 33 and parts_gdf["parte_id"].is_unique and str(parts_gdf.crs) == "EPSG:9377",
        f"capa=partes, filas={len(parts_gdf)}, partes únicas={parts_gdf['parte_id'].nunique()}, CRS={parts_gdf.crs}",
    )
    status(checks, "Fragmentos conservados", len(fragments) == 6 and fragments["parte_id"].is_unique,
           f"filas={len(fragments)}, partes únicas={fragments['parte_id'].nunique()}")
    status(checks, "Zonas de concentración", len(zones) == 439 and int(zones["prioritaria"].sum()) == 12,
           f"zonas={len(zones)}, prioritarias={int(zones['prioritaria'].sum())}")
    status(checks, "Eventos sin zona", int(facts["zona_id"].isna().sum()) == 44,
           f"sin zona={int(facts['zona_id'].isna().sum())}")

    missing_m = [name for name in EXPECTED_M if not (PQ / name).is_file()]
    status(checks, "Consultas M separadas", not missing_m,
           "todas presentes" if not missing_m else f"faltantes={missing_m}")
    forbidden = ("PostgreSQL.Database", "Sql.Database", "Odbc.DataSource", "Web.Contents", "Value.NativeQuery")
    m_sources = {path.name: path.read_text(encoding="utf-8") for path in PQ.glob("*.m*")}
    forbidden_hits = {
        name: [term for term in forbidden if term in content]
        for name, content in m_sources.items()
        if any(term in content for term in forbidden)
    }
    status(checks, "Consultas M sin fuentes prohibidas", not forbidden_hits,
           "sin PostgreSQL/SQL/API" if not forbidden_hits else str(forbidden_hits))
    m_without_template = {name: content for name, content in m_sources.items() if not name.endswith(".template")}
    m_structurally_valid = all(
        m_delimiters_balanced(content)
        and ("=>" in content or ("let" in content and "in" in content))
        for content in m_without_template.values()
    )
    status(
        checks,
        "Estructura léxica de consultas M",
        m_structurally_valid,
        "paréntesis, llaves, corchetes y estructura let/in o función revisados; no sustituye Power BI Desktop",
    )
    required_m_terms = {
        "10_StgHechos.m": ("8332", "evento_id"),
        "12_StgConFecha.m": ("JoinKind.LeftOuter", "CoincidenciasAuxiliar", "zona_id_modelo"),
        "28_DimIdsCongelados.m": ("ids_cierre_v1.json", "604"),
        "40_ValidacionCierre.m": ("IDs congelados principal exactos", "7684"),
        "41_ControlCierreEstricto.m": ("MM45_CIERRE_INVALIDO",),
    }
    for filename, terms in required_m_terms.items():
        content = m_sources.get(filename, "")
        status(checks, f"Contenido M: {filename}", all(term in content for term in terms),
               f"términos verificados={list(terms)}")

    dax = DAX.read_text(encoding="utf-8") if DAX.is_file() else ""
    missing_measures = [measure for measure in EXPECTED_MEASURES if re.search(rf"(?m)^{re.escape(measure)}\s*=", dax) is None]
    status(checks, "Medidas DAX requeridas", not missing_measures,
           f"medidas esperadas={len(EXPECTED_MEASURES)}; faltantes={missing_measures}")
    status(checks, "Paréntesis DAX balanceados", parentheses_balanced(dax),
           "comprobación estática; no reemplaza la compilación en Desktop")
    status(checks, "DAX con control de 604 IDs", "Integridad IDs principal" in dax and "DimIdsCongelados" in dax,
           "medida de comparación exacta presente")

    project_files = [path for extension in ("*.pbix", "*.pbip", "*.pbit") for path in ROOT.rglob(extension)]
    status(
        checks,
        "PBIX/PBIP/PBIT",
        bool(project_files),
        "No existe un archivo Power BI real en el repositorio; el bloqueo queda documentado."
        if not project_files else f"archivos={project_files}",
        blocked=not bool(project_files),
    )

    after = {str(path.relative_to(ROOT)): sha256(path) for path in protected}
    status(checks, "Fuentes protegidas sin escritura", before == after,
           "hashes iguales antes/después de la validación")

    passed = sum(item["estado"] == "OK" for item in checks)
    failed = sum(item["estado"] == "ERROR" for item in checks)
    blocked = sum(item["estado"] == "BLOQUEADO" for item in checks)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Validación estática; no compila M/DAX ni controla Power BI Desktop.",
        "summary": {"passed": passed, "failed": failed, "blocked": blocked, "total": len(checks)},
        "checks": checks,
        "source_hashes": before,
        "pbip_status": "BLOQUEADO: no se genera PBIP/PBIX sin apertura, refresh y validación en Power BI Desktop.",
    }
    (OUT / "validacion_estatica_powerbi.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Validación estática de recursos Power BI",
        "",
        f"Resultado: **{passed}/{len(checks)} controles OK**; {failed} error(es) y {blocked} bloqueo(s).",
        "",
        "Esta ejecución leyó fuentes locales y escribió únicamente este informe y su JSON asociado. No abre ni controla Power BI Desktop; por tanto, no certifica la compilación de M/DAX, relaciones, render o refresh en Desktop.",
        "",
        "| Control | Estado | Detalle |",
        "|---|---|---|",
    ]
    lines.extend(f"| {item['control']} | {item['estado']} | {item['detalle']} |" for item in checks)
    lines.extend([
        "",
        "## Estado PBIP/PBIX",
        "",
        payload["pbip_status"],
        "",
        "Los recursos manuales están en `powerbi/implementation/powerquery/` y `powerbi/implementation/dax/` desde la raíz del proyecto; consulte la [guía Power BI](powerbi.md).",
    ])
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "validacion_estatica_powerbi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
