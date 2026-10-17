"""Crea PDF profesionales equivalentes a los documentos finales editables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "final"
FACTS = ROOT / "powerbi" / "geospatial" / "hechos_siniestros.csv"
MAP_CORRIDOR = ROOT / "reports" / "mapa_corredor_siniestros_carrera45_50m.png"
DISTANCE_PLOT = ROOT / "reports" / "distribucion_distancias_siniestros_carrera45.png"

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#007C83")
SLATE = colors.HexColor("#536779")
LIGHT = colors.HexColor("#EAF2F4")
GRID = colors.HexColor("#D9E2E8")


def styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=sample["Title"], fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=colors.black, spaceAfter=6),
        "subtitle": ParagraphStyle("subtitle", parent=sample["Normal"], fontName="Helvetica", fontSize=10.5, leading=14, textColor=SLATE, spaceAfter=13),
        "h1": ParagraphStyle("h1", parent=sample["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.black, spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("body", parent=sample["BodyText"], fontName="Helvetica", fontSize=9.5, leading=12.3, textColor=colors.HexColor("#202B36"), spaceAfter=5),
        "bullet": ParagraphStyle("bullet", parent=sample["BodyText"], fontName="Helvetica", fontSize=9.2, leading=11.7, leftIndent=13, firstLineIndent=-7, spaceAfter=2),
        "caption": ParagraphStyle("caption", parent=sample["Normal"], fontName="Helvetica-Oblique", fontSize=7.4, leading=9, textColor=SLATE, alignment=TA_CENTER, spaceAfter=4),
        "small": ParagraphStyle("small", parent=sample["Normal"], fontName="Helvetica", fontSize=8, leading=10, textColor=SLATE),
    }


def draw_footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(SLATE)
    canvas.drawCentredString(letter[0] / 2, 0.72 * cm, f"MoviManrique45  |  Comuna 3 Manrique  |  Página {document.page}")
    canvas.restoreState()


def doc(path: Path) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=1.65 * cm,
        rightMargin=1.65 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.4 * cm,
        title=path.stem.replace("_", " "),
        author="MoviManrique45",
    )


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def data_table(headers: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    body = [[p(h, "small") for h in headers]]
    body += [[p(v, "small") for v in row] for row in rows]
    table = Table(body, colWidths=[w * cm for w in widths], repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for idx in range(1, len(body)):
        if idx % 2 == 0:
            commands.append(("BACKGROUND", (0, idx), (-1, idx), LIGHT))
    table.setStyle(TableStyle(commands))
    return table


def metrics() -> dict[str, int]:
    facts = pd.read_csv(FACTS)
    c = facts["categoria_analisis"].value_counts().to_dict()
    return {"total": len(facts), "principal": int(c["principal_50m"]), "borde": int(c["sensibilidad_borde"]), "revision": int(c["revision_territorial"]), "resto": int(c["resto_manrique"])}


def title_block(title: str, subtitle: str) -> list:
    return [p(title, "title"), p(subtitle, "subtitle")]


def figure(path: Path, height_cm: float, caption: str) -> list:
    if not path.exists():
        return []
    image = Image(str(path))
    ratio = image.imageWidth / image.imageHeight
    image.drawHeight = height_cm * cm
    image.drawWidth = image.drawHeight * ratio
    max_width = 16.7 * cm
    if image.drawWidth > max_width:
        image.drawWidth = max_width
        image.drawHeight = image.drawWidth / ratio
    return [image, p(caption, "caption")]


def build_technical(d: dict[str, int]) -> None:
    out = OUT / "MoviManrique45_Documento_Tecnico.pdf"
    story = title_block("Documento técnico MoviManrique45", "Seguridad vial y accesibilidad en la Carrera 45 de la Comuna 3 Manrique")
    story += [
        p("MoviManrique45 organiza evidencia histórica de siniestros para apoyar la lectura territorial de la Carrera 45. El resultado principal es un corredor analítico estricto de 50 metros, limitado por el polígono oficial de Manrique y separado de los casos de borde o revisión."),
        p("Resultados principales", "h1"),
        data_table(["Indicador", "Resultado"], [
            ["Siniestros nominales de Comuna 3", f"{d['total']:,}".replace(",", ".")],
            ["Corredor territorial estricto de 50 m", str(d["principal"])],
            ["Sensibilidad de borde", str(d["borde"])],
            ["Revisión territorial", str(d["revision"])],
            ["Resto de Manrique", f"{d['resto']:,}".replace(",", ".")],
            ["Eje vial", "26 segmentos y 1.698,67 m"],
            ["Concentraciones exploratorias", "439 celdas y 12 zonas"],
        ], [10.5, 6.0]),
        p("El indicador de 604 no equivale a los 644 registros obtenidos por proximidad geométrica simple de hasta 50 metros. Los 40 casos adicionales cercanos al borde territorial se conservan como sensibilidad y no amplían el indicador oficial."),
        PageBreak(),
        p("Problema territorial y objetivo", "h1"),
        p("La seguridad vial y la accesibilidad peatonal requieren evidencia espacial que distinga la cercanía a un eje vial de la pertenencia territorial. El proyecto se concentra exclusivamente en la Comuna 3 Manrique y no incorpora segmentos externos por su atributo nominal cuando su geometría queda fuera del polígono oficial."),
        p("Fuentes y metodología", "h1"),
    ]
    story += [p(f"• {item}", "bullet") for item in [
        "Siniestros viales históricos de Medellín, filtrados reproduciblemente para Comuna 3.",
        "Malla vial y límite oficial de Manrique provenientes de la Alcaldía de Medellín.",
        "Eje de Carrera 45 recortado contra el límite territorial, con 26 segmentos válidos.",
        "Buffer analítico de 50 m recortado territorialmente. La distancia representa proximidad, no causalidad.",
        "Categorización exclusiva: corredor principal, sensibilidad de borde, revisión territorial y resto de Manrique.",
        "Cuadrícula de 100 m para concentraciones históricas exploratorias. No estima riesgo ni significancia estadística.",
    ]]
    story += [
        p("Arquitectura tecnológica", "h1"),
        p("Python, pandas, GeoPandas y Shapely procesan datos locales. GeoPackage y GeoJSON preservan capas geográficas. Un dashboard web estático consume una vista derivada validada y QGIS conserva el proyecto de inspección geográfica. Power BI cuenta con recursos de implementación preparados, pero no con un archivo PBIX o PBIP validado."),
        PageBreak(),
        p("Resultados geoespaciales", "h1"),
        *figure(MAP_CORRIDOR, 16.2, "Corredor analítico de 50 m, eje definitivo y siniestros seleccionados. Fuente: resultados geoespaciales del proyecto."),
        p("La delimitación territorial evita interpretar como parte del corredor los registros próximos al eje pero ubicados fuera del polígono oficial de Manrique. Se preservan seis fragmentos menores de un metro para mantener trazabilidad del recorte geométrico."),
        PageBreak(),
        p("Dashboard y análisis exploratorio", "h1"),
        *figure(DISTANCE_PLOT, 8.3, "Distribución de distancias al eje de Carrera 45. Fuente: análisis de distancias del proyecto."),
        p("El dashboard local presenta indicadores, evolución anual, distribución por gravedad y tipo, filtros por año, barrio y clasificación, además del geovisor. La aplicación bloquea la exportación si cambian los 8.332 eventos o los 604 IDs principales."),
        p("Alcance analítico e IA", "h1"),
        p("El proyecto no implementa un modelo de aprendizaje automático ni una predicción de siniestros. La grilla de concentraciones constituye análisis geoespacial descriptivo. Faltan variables de exposición, aforos, velocidades observadas, infraestructura detallada y validación prospectiva para justificar un modelo predictivo responsable."),
        PageBreak(),
        p("Limitaciones y recomendaciones", "h1"),
    ]
    story += [p(f"• {item}", "bullet") for item in [
        "Los registros históricos no sustituyen inspección de campo, aforos ni auditoría de accesibilidad.",
        "La ubicación válida no garantiza precisión absoluta del geocodificado.",
        "Las zonas exploratorias no son tasas de riesgo, puntos negros oficiales ni evidencia de causalidad.",
        "Los cuatro registros de revisión territorial requieren contraste con fuentes autorizadas antes de reclasificarlos.",
    ]]
    story += [
        p("Las propuestas preliminares incluyen revisión de cruces peatonales, visibilidad, continuidad de andenes, señalización, iluminación, gestión de velocidad y accesibilidad universal. La evaluación de reductores, señalización, protección de personas mayores y personas con discapacidad requiere diseño autorizado, participación comunitaria y validación de la autoridad competente."),
        p("Las recomendaciones no acreditan obra ejecutada, aprobación institucional ni diseño de ingeniería. El proyecto entrega una base reproducible para priorizar futuras revisiones técnicas."),
    ]
    doc(out).build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


def build_executive(d: dict[str, int]) -> None:
    out = OUT / "MoviManrique45_Resumen_Ejecutivo.pdf"
    story = title_block("Resumen ejecutivo MoviManrique45", "Seguridad vial y accesibilidad de la Carrera 45 en la Comuna 3 Manrique")
    story += [
        p("MoviManrique45 reúne datos históricos de siniestros y análisis geoespacial para apoyar la priorización técnica de la movilidad y accesibilidad peatonal en la Carrera 45. El prototipo local ofrece indicadores, filtros y un geovisor con resultados trazables."),
        data_table(["Resultado", "Valor"], [
            ["Siniestros analizados en Comuna 3", f"{d['total']:,}".replace(",", ".")],
            ["Casos del corredor territorial estricto", str(d["principal"])],
            ["Casos de sensibilidad de borde", str(d["borde"])],
            ["Casos de revisión territorial", str(d["revision"])],
            ["Zonas prioritarias exploratorias", "12"],
        ], [11.0, 5.5]),
        p("Qué significa el corredor", "h1"),
        p("El corredor se construyó con un buffer de 50 metros alrededor del eje definitivo de Carrera 45 y se recortó al límite oficial de Manrique. Por ello, los 604 casos principales son diferentes de los 644 eventos que aparecen al medir solo la proximidad geométrica al eje."),
        p("Uso recomendado", "h1"),
        p("El tablero permite revisar años, barrios y categorías territoriales. Las 12 zonas exploratorias orientan revisiones de cruces, visibilidad, señalización, continuidad de andenes, velocidad y accesibilidad. Las decisiones de inversión requieren visita de campo, diseño de ingeniería, participación comunitaria y validación institucional."),
        p("Límites", "h1"),
        p("Los datos describen siniestros históricos. No calculan tasas de riesgo, no atribuyen causalidad a la vía y no predicen accidentes. El proyecto conserva 40 casos de borde y cuatro registros de revisión fuera del indicador principal para mantener transparencia territorial."),
    ]
    doc(out).build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


def build_budget() -> None:
    out = OUT / "MoviManrique45_Presupuesto_Seis_Meses.pdf"
    story = title_block("Presupuesto estimado MoviManrique45", "Proyección de implementación integral durante seis meses")
    story += [
        p("Las cifras son estimaciones de planeación para un piloto integral. No constituyen cotizaciones, ofertas comerciales ni presupuesto aprobado. El total no incorpora obras físicas, las cuales requieren estudios, diseños, permisos y contratación."),
        p("Estimación de seis meses", "h1"),
        data_table(["Rubro", "Supuesto de planeación", "COP"], [
            ["Dirección técnica y gestión", "Dedicación parcial durante seis meses", "54.000.000"],
            ["Ingeniería de datos y geoespacial", "Dos perfiles parciales durante seis meses", "96.000.000"],
            ["Diseño y desarrollo de visualización", "Un perfil parcial durante cinco meses", "35.000.000"],
            ["Validación técnica y QA", "Revisión independiente y pruebas", "22.000.000"],
            ["Trabajo de campo y participación", "Aforos, accesibilidad y talleres, sujeto a permisos", "48.000.000"],
            ["Infraestructura y licencias", "Servicios locales o nube, respaldo y herramientas", "18.000.000"],
            ["Contingencia", "10 % de costos anteriores", "27.300.000"],
            ["Total estimado sin obra física", "", "300.300.000"],
        ], [4.3, 8.2, 3.0]),
        p("Intervenciones físicas", "h1"),
        p("Las intervenciones físicas forman un rubro separado y no se cuantifican con los datos actuales. La definición de cruces, señalización, accesibilidad, calmado de tráfico u otras obras requiere inspección de campo, estudios de tránsito, diseño autorizado y proceso contractual."),
        p("Condiciones de uso", "h1"),
        p("La estimación sirve para planeación inicial. Cualquier decisión presupuestal debe actualizar salarios, licencias, precios de infraestructura, alcance del trabajo de campo y requerimientos de la autoridad competente."),
    ]
    doc(out).build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


def build_manual() -> None:
    out = OUT / "MoviManrique45_Manual_Demostracion.pdf"
    story = title_block("Manual de demostración MoviManrique45", "Ejecución local del dashboard y verificación de resultados")
    story += [
        p("Requisitos", "h1"),
        p("Use el entorno virtual incluido o cree uno con las dependencias declaradas. La demostración web no necesita conexión a servicios externos ni acceso a PostgreSQL."),
        p("Procedimiento", "h1"),
        data_table(["Paso", "Acción"], [
            ["1", "Desde la raíz del proyecto ejecute scripts\\iniciar_demo.ps1."],
            ["2", "Abra http://localhost:8501 en un navegador."],
            ["3", "Revise los indicadores 8.332, 604, 40 y 4."],
            ["4", "Aplique filtros por año, barrio y clasificación."],
            ["5", "Explore el geovisor, sus capas, leyenda e información de zonas."],
            ["6", "Ejecute la suite de pruebas indicada por el manual del repositorio antes de una presentación formal."],
        ], [1.4, 14.3]),
        p("Criterios de demostración", "h1"),
        p("El indicador principal corresponde a 604 siniestros dentro del corredor territorial estricto de 50 metros. Los 40 casos de sensibilidad de borde y cuatro de revisión territorial aparecen separados. La proximidad no demuestra causalidad y las zonas exploratorias no son tasas de riesgo."),
        p("Power BI", "h1"),
        p("Los recursos de Power Query, DAX y modelo están listos para importación manual. No presente Power BI como terminado hasta crear y validar un PBIX o PBIP en Power BI Desktop."),
    ]
    doc(out).build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


STYLES = styles()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = metrics()
    build_technical(d)
    build_executive(d)
    build_budget()
    build_manual()
    for file in sorted(OUT.glob("*.pdf")):
        print(file)


if __name__ == "__main__":
    main()
