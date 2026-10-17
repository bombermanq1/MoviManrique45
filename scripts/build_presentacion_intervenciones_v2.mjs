/**
 * Construye una versión nueva de la presentación final de MoviManrique45.
 * Usa exclusivamente resultados, mapas y conteos locales ya validados.
 * No modifica insumos RAW, geometrías, PostgreSQL ni los entregables previos.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "C:\\Users\\matth\\OneDrive\\Escritorio\\ITM\\movimanrique45";
const ESTILO = (process.env.MOVIMANRIQUE_ESTILO || "v2").trim().toLowerCase();
const ES_V3 = ESTILO === "v3";
const ETIQUETA_ARCHIVO = ES_V3 ? "v3_Textos_Claros" : "v2_Intervenciones";
const RUNTIME_NODE_MODULES = "C:\\Users\\matth\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const ARTIFACT_TOOL = path.join(RUNTIME_NODE_MODULES, "@oai", "artifact-tool", "dist", "artifact_tool.mjs");
const SKILL = "C:\\Users\\matth\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.1015.12040\\skills\\presentations";
const PYTHON = "C:\\Users\\matth\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const BUILD = path.join(ROOT, ".build", ES_V3 ? "presentacion_textos_claros_v3" : "presentacion_intervenciones_v2");
const PREVIEWS = path.join(BUILD, "previews");
const STAGING = path.join(BUILD, ".codex-finalizer");
const FINAL = path.join(ROOT, "deliverables", "final", ES_V3 ? "v3_textos_claros" : "v2", `MoviManrique45_Presentacion_${ETIQUETA_ARCHIVO}.pptx`);
const W = 1280;
const H = 720;
const M = 64;
const FONT = "Arial";
const C = {
  navy: "#0F172A",
  blue: "#2563EB",
  teal: "#14B8A6",
  white: "#FFFFFF",
  pale: "#F1F5F9",
  ink: "#172033",
  muted: "#52616B",
  border: "#CBD5E1",
  amber: "#D97706",
  red: "#BE123C",
  bluePale: "#E8F0FF",
};

function texto(versionV2, versionV3) {
  return ES_V3 ? versionV3 : versionV2;
}

process.env.RUNTIME_NODE_MODULES = RUNTIME_NODE_MODULES;
const { Presentation, PresentationFile } = await import(pathToFileURL(ARTIFACT_TOOL).href);

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function imageBlob(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function json(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

function text(slide, value, left, top, width, height, style = {}) {
  const box = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  box.text = value;
  box.text.style = { typeface: FONT, fontSize: 18, color: C.ink, ...style };
  return box;
}

function line(slide, left, top, width, height, fill) {
  slide.shapes.add({
    geometry: "rect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill, width: 0 },
  });
}

function panel(slide, left, top, width, height, fill = C.white) {
  return slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: C.border, width: 1 },
    borderRadius: "rounded-xl",
  });
}

function header(slide, title, subtitle = "") {
  text(slide, "MOVIMANRIQUE45", M, 31, 245, 18, {
    fontSize: 11, bold: true, color: C.blue,
  });
  text(slide, title, M, 60, 1090, 54, {
    fontSize: 31, bold: true, color: C.navy,
  });
  if (subtitle) {
    text(slide, subtitle, M, 124, 1090, 24, { fontSize: 14, color: C.muted });
  }
  line(slide, M, 157, W - (M * 2), 2, C.blue);
}

function footer(slide, number) {
  line(slide, M, 681, W - (M * 2), 1, C.border);
  text(slide, "Comuna 3 - Manrique | Evidencia territorial reproducible", M, 690, 680, 15, {
    fontSize: 10, color: C.muted,
  });
  text(slide, String(number).padStart(2, "0"), 1169, 690, 47, 15, {
    fontSize: 10, bold: true, color: C.blue,
  });
}

function notes(slide, source, detail) {
  slide.speakerNotes.text = [`Fuente: ${source}`, detail];
  slide.speakerNotes.setVisible(true);
}

function bullets(slide, items, left, top, width, fontSize = 16, color = C.ink, gap = 13) {
  const content = items.map((item) => `• ${item}`).join("\n\n");
  text(slide, content, left, top, width, items.length * (fontSize + gap + 10), {
    fontSize, color,
  });
}

async function image(slide, filePath, left, top, width, height, alt, fit = "contain") {
  slide.images.add({
    blob: await imageBlob(filePath),
    contentType: "image/png",
    alt,
    fit,
    position: { left, top, width, height },
    geometry: "roundRect",
    borderRadius: "rounded-xl",
  });
}

function styleTable(table, rows, columns, total = false) {
  table.styleOptions = { headerRow: true, bandedRows: true, totalRow: total };
  table.borders.assign({ style: "solid", fill: C.border, width: 1 });
  for (let col = 0; col < columns; col += 1) {
    table.getCell(0, col).fill = C.navy;
    table.getCell(0, col).text.style = {
      typeface: FONT, fontSize: 12, bold: true, color: C.white,
    };
    if (total) {
      table.getCell(rows - 1, col).fill = "#D5F5F0";
      table.getCell(rows - 1, col).text.style = {
        typeface: FONT, fontSize: 12, bold: true, color: C.navy,
      };
    }
  }
  for (let row = 1; row < rows - (total ? 1 : 0); row += 1) {
    for (let col = 0; col < columns; col += 1) {
      table.getCell(row, col).text.style = { typeface: FONT, fontSize: 12, color: C.ink };
    }
  }
}

function metric(slide, value, label, left, top, color = C.blue) {
  text(slide, String(value), left, top, 112, 42, { fontSize: 31, bold: true, color });
  text(slide, label, left + 122, top + 7, 166, 36, { fontSize: 13, color: C.muted });
}

async function main() {
  const exists = await fs.access(FINAL).then(() => true).catch(() => false);
  if (exists) {
    throw new Error(`No se sobrescribe una entrega final existente: ${FINAL}`);
  }
  await fs.mkdir(PREVIEWS, { recursive: true });
  await fs.mkdir(STAGING, { recursive: true });

  const dashboard = await json(path.join(ROOT, "web", "data", "dashboard.json"));
  const interventionData = await json(path.join(ROOT, "web", "data", "intervenciones.json"));
  const events = dashboard.eventos;
  const annual = [...new Map(events.map((event) => [event.anio, 0])).keys()]
    .sort((a, b) => a - b)
    .map((year) => [String(year), events.filter((event) => event.anio === year).length]);
  const categories = events.reduce((acc, event) => {
    acc[event.categoria_analisis] = (acc[event.categoria_analisis] || 0) + 1;
    return acc;
  }, {});
  const topZones = [...interventionData.zonas]
    .sort((a, b) => b.diagnostico_historico.registros_historicos - a.diagnostico_historico.registros_historicos)
    .slice(0, 5);

  const axisMap = path.join(ROOT, "reports", "mapa_carrera45_manrique_definitiva.png");
  const corridorMap = path.join(ROOT, "reports", "mapa_corredor_siniestros_carrera45_50m.png");
  const distanceChart = path.join(ROOT, "reports", "distribucion_distancias_siniestros_carrera45.png");
  const qgisMap = path.join(ROOT, "reports", "geospatial", "qgis_final_preview.png");
  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 1. Portada
  {
    const slide = deck.slides.add();
    slide.background.fill = C.navy;
    await image(slide, axisMap, 762, 0, 518, 720, "Eje definitivo de Carrera 45 dentro de Manrique", "cover");
    slide.shapes.add({
      geometry: "rect",
      position: { left: 735, top: 0, width: 545, height: 720 },
      fill: "#0F172ACC",
      line: { style: "solid", fill: "none", width: 0 },
    });
    text(slide, "MOVIMANRIQUE45", 72, 82, 255, 25, { fontSize: 14, bold: true, color: C.teal });
    text(slide, "Seguridad vial y accesibilidad en la Carrera 45", 72, 139, 592, 144, {
      fontSize: 43, bold: true, color: C.white,
    });
    text(slide, texto(
      "Comuna 3 - Manrique, Medellín\nAnalítica territorial con trazabilidad geoespacial",
      "Comuna 3 - Manrique, Medellín\nInformación territorial para entender y revisar el corredor.",
    ), 72, 325, 560, 62, {
      fontSize: 20, color: "#DDE9FB",
    });
    text(slide, texto("Versión 2 | Intervenciones exploratorias", "Versión 3 | Información para la revisión de campo"), 72, 548, 500, 22, { fontSize: 15, color: C.teal });
    text(slide, texto("Cierre validado: 8.332 siniestros | 604 IDs del corredor estricto", "Base validada: 8.332 siniestros | 604 dentro del corredor de 50 m"), 72, 594, 620, 26, {
      fontSize: 14, color: "#DDE9FB",
    });
    notes(slide, "reports/mapa_carrera45_manrique_definitiva.png; reports/geospatial/cierre_tecnico.md", "El eje definitivo contiene 26 segmentos y se limita al polígono oficial de Manrique.");
  }

  // 2. Problema territorial
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    header(slide, texto("Problema territorial", "¿Qué estamos revisando?"), texto(
      "El análisis delimita el corredor con geometría oficial y conserva sus casos de borde.",
      "El corredor se delimitó con el límite oficial de Manrique y conserva los casos cercanos al borde.",
    ));
    text(slide, "Carrera 45 dentro de Manrique", 64, 193, 370, 31, { fontSize: 20, bold: true, color: C.navy });
    bullets(slide, [
      texto("La malla vial declaraba un CRS distinto a sus coordenadas reales. El proyecto corrigió esa interpretación solo en memoria.", "La malla vial tenía una diferencia entre el CRS declarado y sus coordenadas. Se trató solo en memoria, sin cambiar la fuente original."),
      texto("El eje se recortó contra el límite oficial de Comuna 3 - Manrique y conserva 26 segmentos, 33 partes y seis fragmentos menores de un metro.", "El eje se recortó con el límite oficial de la Comuna 3 - Manrique y conserva 26 segmentos, 33 partes y seis fragmentos menores de un metro."),
      texto("El corredor analítico de 50 m representa proximidad espacial. No demuestra causalidad ni atribuye un siniestro a la vía.", "El corredor de 50 m muestra cercanía al eje. No demuestra causalidad ni atribuye un siniestro a la vía."),
    ], 64, 245, 430, 16, C.ink, 14);
    await image(slide, corridorMap, 540, 178, 676, 440, "Corredor de 50 metros, Manrique y siniestros seleccionados", "contain");
    text(slide, "Fuente: productos geoespaciales validados del proyecto", 540, 632, 560, 16, { fontSize: 11, color: C.muted });
    footer(slide, 2);
    notes(slide, "reports/mapa_corredor_siniestros_carrera45_50m.png; reports/geospatial/cierre_tecnico.md", "La imagen presenta el corredor de 50 m recortado al límite oficial de Manrique.");
  }

  // 3. Objetivos
  {
    const slide = deck.slides.add();
    slide.background.fill = C.pale;
    header(slide, texto("Objetivos", "¿Para qué sirve?"), texto(
      "Una plataforma local para revisar evidencia histórica antes de proponer actuaciones físicas.",
      "Una herramienta local para revisar registros históricos antes de pensar en posibles soluciones.",
    ));
    const objectives = [
      [texto("Delimitación", "Territorio"), texto("Definir la Carrera 45 dentro del territorio oficial de Manrique.", "Ubicar la Carrera 45 dentro del territorio oficial de Manrique.")],
      ["Trazabilidad", texto("Mantener categorías exclusivas, IDs congelados, hashes y pruebas reproducibles.", "Conservar datos, categorías y pruebas que permitan revisar el resultado.")],
      [texto("Exploración", "Consulta"), texto("Permitir filtros, geovisor y fichas de zonas sin convertirlas en decisiones de obra.", "Usar filtros, mapa y fichas de zonas sin convertirlos en decisiones de obra.")],
    ];
    objectives.forEach((item, index) => {
      const left = 64 + index * 387;
      line(slide, left, 226, 7, 274, index === 0 ? C.blue : index === 1 ? C.teal : C.amber);
      text(slide, `0${index + 1}`, left + 30, 238, 55, 31, { fontSize: 20, bold: true, color: C.blue });
      text(slide, item[0], left + 30, 301, 284, 32, { fontSize: 23, bold: true, color: C.navy });
      text(slide, item[1], left + 30, 364, 300, 96, { fontSize: 17, color: C.muted });
    });
    text(slide, texto(
      "Alcance actual: analítica descriptiva y geoespacial. Power BI nativo y aprendizaje automático predictivo permanecen fuera del cierre validado.",
      "Alcance actual: análisis descriptivo y geoespacial. Power BI nativo y modelos predictivos no hacen parte de este cierre.",
    ), 64, 555, 1110, 38, {
      fontSize: 16, bold: true, color: C.navy,
    });
    footer(slide, 3);
    notes(slide, "README.md; reports/estado_mvp.md; reports/ia_exploratoria.md", "La plataforma no declara un modelo predictivo ni un informe Power BI nativo validado.");
  }

  // 4. Fuentes y trazabilidad
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    header(slide, texto("Fuentes de datos y trazabilidad", "¿Con qué información trabajamos?"), texto(
      "La vista web deriva de insumos validados y no altera los archivos RAW.",
      "La vista web usa insumos validados y no modifica los archivos originales.",
    ));
    const rows = [
      ["Fuente", "Uso en el proyecto", "Resultado validado"],
      ["Siniestros viales", "Puntos y atributos de Comuna 3", "8.332 registros entre 2019 y 2025"],
      ["Malla vial oficial", "Eje definitivo de Carrera 45", "26 segmentos | 1.698,67 m"],
      ["Límite territorial", "Recorte y control espacial", "Comuna 3 - Manrique en EPSG:9377"],
      ["Capas derivadas", texto("Geovisor y zonas exploratorias", "Geovisor y zonas identificadas"), "439 celdas | 12 zonas"],
    ];
    const table = slide.tables.add({
      rows: rows.length, columns: 3, left: 64, top: 205, width: 760, height: 284,
      values: rows, columnWidths: [200, 270, 290],
    });
    styleTable(table, rows.length, 3);
    panel(slide, 866, 205, 350, 284, C.pale);
    text(slide, texto("Cierre de categorías", "Cómo se organizan los registros"), 896, 235, 300, 30, { fontSize: 19, bold: true, color: C.navy });
    metric(slide, 604, texto("corredor estricto", "dentro del corredor (50 m)"), 896, 289, C.teal);
    metric(slide, 40, texto("sensibilidad de borde", "cerca del límite"), 896, 350, C.amber);
    metric(slide, 4, texto("revisión territorial", "ubicación por revisar"), 896, 411, C.red);
    text(slide, `${categories.resto_manrique ?? 7684} ${texto("registros restantes", "otros registros de Manrique")}`, 64, 545, 360, 23, { fontSize: 17, bold: true, color: C.navy });
    text(slide, texto("Los 644 casos por proximidad geométrica simple no sustituyen los 604 IDs oficiales del cierre.", "Los 644 casos por proximidad geométrica simple no sustituyen los 604 registros del indicador principal."), 405, 546, 760, 24, { fontSize: 16, bold: true, color: C.red });
    footer(slide, 4);
    notes(slide, "web/data/dashboard.json; reports/geospatial/cierre_tecnico.md; src/geospatial/ids_cierre_v1.json", "La presentación diferencia la proximidad geométrica simple de la clasificación de cierre con IDs oficiales.");
  }

  // 5. Metodología
  {
    const slide = deck.slides.add();
    slide.background.fill = C.pale;
    header(slide, texto("Metodología reproducible", "Cómo se construyó el análisis"), texto(
      "El flujo conserva evidencia y reglas explícitas desde la ingesta hasta la exploración local.",
      "Del dato original al geovisor, con reglas que se pueden revisar.",
    ));
    const stages = [
      [texto("Ingesta", "Datos"), texto("Fuentes oficiales y copia RAW.", "Fuentes oficiales y copia original.")],
      ["Validación", "CRS, atributos y geometrías."],
      [texto("Recorte", "Territorio"), texto("Eje y corredor dentro de Manrique.", "Eje y corredor dentro de Manrique.")],
      ["Clasificación", texto("IDs exclusivos y casos de borde.", "Registros dentro, cerca del límite y por revisar.")],
      [texto("Exploración", "Consulta"), texto("Dashboard, geovisor y fichas.", "Dashboard, mapa y fichas de zonas.")],
    ];
    stages.forEach((stage, index) => {
      const left = 55 + index * 241;
      const color = index === 1 || index === 4 ? C.teal : C.blue;
      line(slide, left, 270, 190, 4, color);
      text(slide, String(index + 1), left, 222, 32, 32, { fontSize: 22, bold: true, color });
      text(slide, stage[0], left, 300, 190, 29, { fontSize: 18, bold: true, color: C.navy });
      text(slide, stage[1], left, 351, 190, 60, { fontSize: 14, color: C.muted });
    });
    text(slide, texto(
      "Regla territorial: ninguna geometría final del corredor se extiende fuera de Comuna 3 - Manrique. Los gaps del eje no se rellenaron artificialmente.",
      "Regla territorial: ninguna parte final del corredor queda fuera de la Comuna 3 - Manrique. Los vacíos entre segmentos no se rellenaron artificialmente.",
    ), 64, 521, 1100, 40, {
      fontSize: 17, bold: true, color: C.navy,
    });
    footer(slide, 5);
    notes(slide, "reports/reporte_carrera45_manrique_definitiva.txt; reports/reporte_corredor_carrera45_50m.txt", "La metodología preserva las geometrías existentes y no conecta segmentos artificialmente.");
  }

  // 6. Resultados
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    header(slide, texto("Resultados descriptivos", "¿Qué encontramos?"), texto(
      "La serie anual y las métricas del cierre se mantienen separadas de cualquier inferencia de riesgo.",
      "Los registros históricos ayudan a ver patrones; no miden por sí solos el riesgo vial.",
    ));
    panel(slide, 64, 183, 730, 426, C.white);
    slide.charts.add("bar", {
      position: { left: 90, top: 213, width: 680, height: 348 },
      title: texto("Siniestros por año en Comuna 3 - Manrique", "Siniestros registrados por año en la Comuna 3 - Manrique"),
      titleTextStyle: { typeface: FONT, fontSize: 16, bold: true, color: C.navy },
      categories: annual.map((row) => row[0]),
      series: [{ name: "Siniestros", values: annual.map((row) => row[1]), fill: C.blue }],
      hasLegend: false,
      barOptions: { direction: "column", grouping: "clustered", gapWidth: 55 },
      dataLabels: { showValue: true, position: "outEnd", textStyle: { typeface: FONT, fontSize: 10, color: C.navy } },
      yAxis: { majorGridlines: { style: "solid", fill: C.border, width: 1 } },
    });
    panel(slide, 835, 183, 381, 426, C.pale);
    text(slide, texto("Indicadores verificables", "Datos principales"), 865, 217, 270, 31, { fontSize: 20, bold: true, color: C.navy });
    metric(slide, 8332, "siniestros analizados", 865, 277, C.blue);
    metric(slide, 604, texto("IDs del corredor estricto", "dentro del corredor (50 m)"), 865, 342, C.teal);
    metric(slide, 439, texto("celdas de concentración", "celdas con registros"), 865, 407, C.amber);
    metric(slide, 12, texto("zonas exploratorias", "zonas identificadas"), 865, 472, C.red);
    footer(slide, 6);
    notes(slide, "web/data/dashboard.json; reports/geospatial/cierre_tecnico.md", `Serie anual calculada desde dashboard.json: ${annual.map(([year, count]) => `${year}=${count}`).join(", ")}.`);
  }

  // 7. Dashboard
  {
    const slide = deck.slides.add();
    slide.background.fill = C.pale;
    header(slide, texto("Dashboard web local", "Consulta el dashboard"), texto(
      "Una vista derivada del cierre permite filtrar, consultar indicadores y navegar las capas geográficas.",
      "Una vista local para filtrar datos, consultar indicadores y recorrer el mapa.",
    ));
    await image(slide, distanceChart, 64, 183, 577, 360, "Distribución de distancias de siniestros al eje de Carrera 45", "contain");
    text(slide, "Distribución de distancias usada como evidencia de apoyo", 64, 558, 560, 17, { fontSize: 11, color: C.muted });
    text(slide, texto("Funciones disponibles", "Qué puede consultar"), 700, 201, 290, 31, { fontSize: 20, bold: true, color: C.navy });
    bullets(slide, [
      texto("Filtros por año, barrio, clase, gravedad y categoría de análisis.", "Filtros por año, barrio, tipo, gravedad y ubicación frente al corredor."),
      texto("Indicadores constantes de 8.332, 604, 40 y 4 registros.", "Indicadores de 8.332, 604, 40 y 4 registros."),
      texto("Gráficas de evolución, gravedad y tipo de siniestro.", "Gráficas por año, gravedad y tipo de siniestro."),
      texto("Geovisor con capas activables, desplazamiento, zoom y selección de zonas.", "Mapa con capas, desplazamiento, zoom y selección de zonas."),
      texto("Módulo de intervenciones con estado inicial Pendiente de inspección.", "Fichas de zonas con estado inicial Pendiente de inspección."),
    ], 700, 259, 460, 16, C.ink, 10);
    text(slide, texto(
      "La interfaz se sirve localmente y lee JSON derivados. No requiere PostgreSQL, internet ni Power BI para la demostración.",
      "La interfaz funciona localmente y lee vistas derivadas. No requiere PostgreSQL, internet ni Power BI para la demostración.",
    ), 64, 617, 1100, 24, { fontSize: 15, bold: true, color: C.navy });
    footer(slide, 7);
    notes(slide, "web/index.html; web/data/dashboard.json; web/data/intervenciones.json; tests/test_dashboard_geovisor.py", "No se presenta esta lámina como una captura del dashboard. La imagen corresponde a un gráfico real del proyecto y las funciones descritas provienen de la interfaz local.");
  }

  // 8. Geovisor y zonas
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    header(slide, texto("Geovisor y zonas exploratorias", "Zonas identificadas"), texto(
      "El mapa conecta el eje, los registros históricos y las 12 celdas seleccionables para revisión territorial.",
      "El mapa conecta el eje, los registros históricos y las 12 zonas que se pueden revisar.",
    ));
    await image(slide, qgisMap, 64, 174, 515, 440, "Vista geoespacial de Manrique con eje, siniestros y celdas", "contain");
    text(slide, "Vista de control geoespacial validada en QGIS", 64, 627, 460, 16, { fontSize: 11, color: C.muted });
    text(slide, texto("Lectura responsable", "Cómo leer las zonas"), 636, 203, 270, 31, { fontSize: 20, bold: true, color: C.navy });
    bullets(slide, [
      texto("Cada zona expone su identificador, ubicación, siniestros históricos, tipos y gravedad disponibles.", "Cada zona muestra su identificador, ubicación, registros históricos, tipos y gravedad disponible."),
      texto("Seleccionar una zona desde el mapa, el listado o la tabla abre la misma ficha y resalta su geometría.", "Seleccionar una zona desde el mapa, el listado o la tabla abre la misma ficha y resalta su ubicación."),
      texto("El orden comparativo usa solo el recuento histórico de cada celda. No equivale a una tasa de riesgo ni a una prioridad institucional.", "El orden usa solo el número histórico de registros de cada celda. No equivale a una tasa de riesgo ni a una prioridad institucional."),
      "La inspección de campo debe verificar velocidades, cruces, visibilidad, accesibilidad y flujos peatonales.",
    ], 636, 259, 525, 16, C.ink, 11);
    footer(slide, 8);
    notes(slide, "reports/geospatial/qgis_final_preview.png; web/data/intervenciones.json", "Las 12 zonas son exploratorias. No reemplazan una auditoría de seguridad vial ni una decisión institucional.");
  }

  // 9. Intervenciones
  {
    const slide = deck.slides.add();
    slide.background.fill = C.pale;
    header(slide, texto("Intervenciones propuestas", "Posibles soluciones"), texto(
      "El módulo organiza evidencia histórica y medidas candidatas para inspección, sin asignar obras ni costos por zona.",
      "El módulo organiza registros históricos y opciones para evaluar, sin asignar obras ni costos por zona.",
    ));
    const zoneRows = [["Orden", "Zona", "Registros", texto("Corredor estricto", "Dentro del corredor"), texto("Eje intersectado", "Tramos del eje")]];
    topZones.forEach((zone, index) => {
      const count = zone.diagnostico_historico.registros_historicos;
      const strict = zone.diagnostico_historico.corredor_estricto_50m;
      const segments = zone.evidencia_geoespacial.segmentos_eje_intersectados_objectid;
      zoneRows.push([String(index + 1), zone.zona_id, String(count), String(strict), segments.length ? segments.join(", ") : "Sin intersección"]);
    });
    const table = slide.tables.add({
      rows: zoneRows.length, columns: 5, left: 64, top: 206, width: 800, height: 287,
      values: zoneRows, columnWidths: [80, 190, 120, 175, 235],
    });
    styleTable(table, zoneRows.length, 5);
    text(slide, texto("Medidas candidatas", "Opciones para evaluar"), 915, 209, 260, 27, { fontSize: 19, bold: true, color: C.navy });
    bullets(slide, [
      "Pasos peatonales seguros, rampas y accesibilidad universal.",
      "Reductores y control de velocidad.",
      "Señalización, visibilidad y protección peatonal.",
    ], 915, 254, 260, 15, C.ink, 9);
    text(slide, texto("Estado de las 12 fichas", "Estado de las 12 zonas"), 915, 429, 250, 20, { fontSize: 14, bold: true, color: C.muted });
    text(slide, "Pendiente de inspección", 915, 462, 265, 31, { fontSize: 20, bold: true, color: C.teal });
    text(slide, texto(
      "Los costos por zona requieren cantidades de obra, diseño y precios unitarios verificables.",
      "Los costos por zona siguen por definir: hacen falta cantidades de obra, diseño y precios unitarios verificables.",
    ), 64, 554, 1088, 38, { fontSize: 16, bold: true, color: C.navy });
    footer(slide, 9);
    notes(slide, "web/data/intervenciones.json; reports/modulo_intervenciones_v1.md", "La tabla se deriva de los cinco mayores recuentos históricos por celda. Cada propuesta permanece pendiente de inspección.");
  }

  // 10. Conclusiones
  {
    const slide = deck.slides.add();
    slide.background.fill = C.navy;
    text(slide, texto("Conclusiones", "¿Qué sigue?"), 64, 68, 400, 50, { fontSize: 34, bold: true, color: C.white });
    text(slide, texto(
      "MoviManrique45 deja una base verificable para revisar la Carrera 45 dentro de la Comuna 3 - Manrique.",
      "MoviManrique45 deja una base verificable para entender y revisar la Carrera 45 dentro de la Comuna 3 - Manrique.",
    ), 64, 146, 970, 38, { fontSize: 20, color: "#DDE9FB" });
    const conclusions = [
      [texto("Datos íntegros", "Datos consistentes"), texto("El cierre conserva 8.332 siniestros, 604 IDs oficiales y los casos de borde y revisión territorial.", "El cierre conserva 8.332 siniestros, 604 registros dentro del corredor y los casos cerca del límite o por revisar.")],
      [texto("Territorio delimitado", "Territorio claro"), texto("El eje definitivo conserva 26 segmentos dentro de Manrique sin rellenar gaps artificialmente.", "El eje definitivo conserva 26 segmentos dentro de Manrique sin rellenar vacíos entre líneas.")],
      [texto("Intervenciones responsables", "Revisión antes de intervenir"), texto("Las 12 fichas muestran evidencia histórica y medidas candidatas, todas pendientes de inspección.", "Las 12 fichas muestran registros históricos y opciones para evaluar; todas siguen pendientes de inspección.")],
    ];
    conclusions.forEach((item, index) => {
      const top = 253 + index * 113;
      line(slide, 67, top + 7, 8, 74, index === 0 ? C.teal : index === 1 ? C.blue : C.amber);
      text(slide, item[0], 102, top, 325, 28, { fontSize: 20, bold: true, color: C.white });
      text(slide, item[1], 450, top, 690, 54, { fontSize: 16, color: "#DDE9FB" });
    });
    text(slide, texto(
      "Siguiente paso: inspección de campo y evaluación institucional antes de cualquier intervención física.",
      "Siguiente paso: revisar en campo y evaluar con las entidades competentes antes de cualquier intervención física.",
    ), 64, 620, 1100, 25, { fontSize: 17, bold: true, color: C.teal });
    notes(slide, "reports/geospatial/cierre_tecnico.md; web/data/intervenciones.json; reports/modulo_intervenciones_v1.md", "La plataforma apoya la preparación de la inspección y no sustituye estudios técnicos, diseños, permisos ni decisiones institucionales.");
  }

  const candidate = path.join(STAGING, `MoviManrique45_Presentacion_${ETIQUETA_ARCHIVO}_candidate.pptx`);
  await (await PresentationFile.exportPptx(deck)).save(candidate);
  const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL, "container_tools", "artifact_tool_utils.mjs")).href);
  const requirements = {
    explicitTotalSlideCount: 10,
    requiredNativeTableOwnerSlides: [4, 9],
    requiredNativeChartOwnerSlides: [6],
    materializeLiteralChartWorkbooks: true,
    nativeChartTargetApplication: "powerpoint",
  };
  const validation = await finalizePresentation({
    ...requirements,
    workspaceDir: ROOT,
    candidatePath: candidate,
    finalPath: FINAL,
    pythonExecutable: PYTHON,
    integrityValidatorPath: path.join(SKILL, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(SKILL, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-bullet-geometry", "--validate-heading-fit",
      "--require-native-table-slide", "4",
      "--require-native-table-slide", "9",
    ],
    requiredNativeTableOwnerSlides: requirements.requiredNativeTableOwnerSlides,
    // PowerPoint aplica Aptos a dos etiquetas internas del gráfico nativo.
    // Se declara junto con Arial para validar exactamente las fuentes observadas.
    fontPolicy: { basis: "design", families: [FONT, "Aptos"] },
    verifyArtifactToolImport: true,
    receiptPath: path.join(STAGING, `MoviManrique45_Presentacion_${ETIQUETA_ARCHIVO}.validation.json`),
  });
  console.log(JSON.stringify({ final: FINAL, slides: deck.slides.items.length, annual, validation }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
