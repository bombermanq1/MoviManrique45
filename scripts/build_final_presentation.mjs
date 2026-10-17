/**
 * Crea el PPTX final del MVP con objetos editables y evidencia local validada.
 * No modifica datos RAW, datasets validados ni geometrías oficiales.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "C:\\Users\\matth\\OneDrive\\Escritorio\\ITM\\movimanrique45";
const BUILD = path.join(ROOT, ".build", "presentation");
const PREVIEWS = path.join(BUILD, "previews");
const FINAL = path.join(ROOT, "deliverables", "final", "MoviManrique45_Presentacion_Final.pptx");
const SKILL = "C:\\Users\\matth\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.1013.11914\\skills\\presentations";
const PYTHON = "C:\\Users\\matth\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const ARTIFACT_TOOL = "C:\\Users\\matth\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\@oai\\artifact-tool\\dist\\artifact_tool.mjs";
const RUNTIME_NODE_MODULES = "C:\\Users\\matth\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const W = 1280;
const H = 720;
const M = 64;
const FONT = "Arial";
const C = {
  ink: "#102A43",
  teal: "#007C91",
  sky: "#0FA3B1",
  pale: "#EDF7F7",
  paper: "#FFFFFF",
  muted: "#52616B",
  border: "#D8E2E7",
  gray: "#F5F8FA",
  red: "#C44536",
};
const annual = [
  ["2019", 1524],
  ["2020", 1142],
  ["2021", 1413],
  ["2022", 1317],
  ["2023", 942],
  ["2024", 849],
  ["2025", 1145],
];
process.env.RUNTIME_NODE_MODULES = RUNTIME_NODE_MODULES;
const { Presentation, PresentationFile } = await import(pathToFileURL(ARTIFACT_TOOL).href);

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function imageBlob(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
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

function frame(slide, left, top, width, height, fill = C.paper) {
  return slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: C.border, width: 1 },
    borderRadius: "rounded-xl",
  });
}

function header(slide, eyebrow, title, subtitle) {
  text(slide, eyebrow.toUpperCase(), M, 34, 500, 20, {
    fontSize: 12, bold: true, color: C.teal,
  });
  text(slide, title, M, 61, 1040, 82, {
    fontSize: 30, bold: true, color: C.ink,
  });
  if (subtitle) {
    text(slide, subtitle, M, 151, 1080, 20, { fontSize: 14, color: C.muted });
  }
}

function footer(slide, number) {
  slide.shapes.add({
    geometry: "rect",
    position: { left: M, top: 682, width: W - (M * 2), height: 1 },
    fill: C.border,
    line: { style: "solid", fill: C.border, width: 0 },
  });
  text(slide, "MoviManrique45 · MVP académico y de portafolio", M, 690, 520, 16, {
    fontSize: 10, color: C.muted,
  });
  text(slide, String(number).padStart(2, "0"), 1172, 690, 44, 16, {
    fontSize: 10, bold: true, color: C.teal,
  });
}

function bullets(slide, items, left, top, width, fontSize = 16, color = C.ink) {
  text(slide, items.map((item) => "• " + item).join("\n\n"), left, top, width,
    items.length * (fontSize + 21), { fontSize, color });
}

async function image(slide, filePath, left, top, width, height, alt, fit = "cover") {
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

function notes(slide, source, detail) {
  slide.speakerNotes.text = ["Fuente: " + source, detail];
  slide.speakerNotes.setVisible(true);
}

function applyTableStyle(table, rows, columns, total = false) {
  table.styleOptions = { headerRow: true, bandedRows: true, totalRow: total };
  table.borders.assign({ style: "solid", fill: C.border, width: 1 });
  for (let col = 0; col < columns; col += 1) {
    table.getCell(0, col).fill = C.ink;
    table.getCell(0, col).text.style = {
      typeface: FONT, fontSize: 13, bold: true, color: C.paper,
    };
    if (total) {
      table.getCell(rows - 1, col).fill = "#D7F0F2";
      table.getCell(rows - 1, col).text.style = {
        typeface: FONT, fontSize: 13, bold: true, color: C.ink,
      };
    }
  }
  for (let row = 1; row < rows - (total ? 1 : 0); row += 1) {
    for (let col = 0; col < columns; col += 1) {
      table.getCell(row, col).text.style = {
        typeface: FONT, fontSize: 12, color: C.ink,
      };
    }
  }
}

async function main() {
  await fs.mkdir(PREVIEWS, { recursive: true });
  await fs.mkdir(path.dirname(FINAL), { recursive: true });
  const exists = await fs.access(FINAL).then(() => true).catch(() => false);
  if (exists) {
    throw new Error("La entrega final ya existe y no se sobrescribirá: " + FINAL);
  }

  const deck = Presentation.create({ slideSize: { width: W, height: H } });
  const axisMap = path.join(ROOT, "reports", "mapa_carrera45_manrique_definitiva.png");
  const corridorMap = path.join(ROOT, "reports", "mapa_corredor_siniestros_carrera45_50m.png");
  const distanceChart = path.join(ROOT, "reports", "distribucion_distancias_siniestros_carrera45.png");
  const qgisMap = path.join(ROOT, "reports", "geospatial", "qgis_final_preview.png");

  // 1. Portada
  {
    const slide = deck.slides.add();
    slide.background.fill = C.ink;
    await image(slide, axisMap, 710, 0, 570, 720, "Eje definitivo de Carrera 45 en Manrique");
    slide.shapes.add({
      geometry: "rect",
      position: { left: 690, top: 0, width: 590, height: 720 },
      fill: "#102A43B8",
      line: { style: "solid", fill: "none", width: 0 },
    });
    text(slide, "MOVIMANRIQUE45", 72, 88, 500, 28, {
      fontSize: 15, bold: true, color: "#90D9DF",
    });
    text(slide, "Seguridad vial y accesibilidad en Carrera 45", 72, 136, 560, 145, {
      fontSize: 41, bold: true, color: C.paper,
    });
    text(slide, "Comuna 3 – Manrique, Medellín\nMVP de analítica territorial con evidencia geoespacial reproducible", 72, 302, 540, 80, {
      fontSize: 20, color: "#D9E9EE",
    });
    text(slide, "Periodo analizado: 2019–2025", 72, 565, 360, 24, {
      fontSize: 15, color: "#D9E9EE",
    });
    text(slide, "Entrega final · 16 de octubre de 2026", 72, 610, 430, 22, {
      fontSize: 13, color: "#90D9DF",
    });
    notes(slide, "reports/mapa_carrera45_manrique_definitiva.png", "Eje definitivo previamente validado: 26 segmentos dentro del límite oficial de Manrique.");
  }

  // 2. Problema
  {
    const slide = deck.slides.add();
    slide.background.fill = C.paper;
    header(slide, "Problema territorial", "El análisis requiere un corredor definido por geometría, no solo por etiquetas", "El proyecto se limita exclusivamente a Comuna 3 – Manrique.");
    frame(slide, 64, 178, 430, 444, C.gray);
    text(slide, "Qué se resolvió", 92, 207, 290, 28, { fontSize: 19, bold: true });
    bullets(slide, [
      "Se validó el eje de Carrera 45 contra el límite oficial de Manrique.",
      "Se preservaron 26 segmentos, 33 partes y seis fragmentos menores de un metro.",
      "La proximidad al eje describe relación espacial; no demuestra causalidad.",
    ], 92, 258, 352, 17);
    await image(slide, corridorMap, 535, 173, 680, 450, "Corredor analítico territorial de 50 metros y siniestros", "contain");
    text(slide, "Corredor analítico recortado al límite oficial de Manrique.", 535, 634, 650, 18, {
      fontSize: 11, color: C.muted,
    });
    footer(slide, 2);
    notes(slide, "reports/mapa_corredor_siniestros_carrera45_50m.png; reports/geospatial/cierre_tecnico.md", "El corredor de 50 m es una delimitación analítica, no una norma vial.");
  }

  // 3. Objetivos
  {
    const slide = deck.slides.add();
    slide.background.fill = C.pale;
    header(slide, "Objetivos", "Convertir datos abiertos en evidencia territorial revisable", "Un MVP para exploración, trazabilidad y comunicación de resultados.");
    const cards = [
      ["01", "Delimitar", "Construir un eje de Carrera 45 limitado por el polígono oficial de Manrique."],
      ["02", "Clasificar", "Separar corredor estricto, sensibilidad de borde, revisión territorial y resto."],
      ["03", "Explorar", "Presentar resultados con dashboard, geovisor y documentación reproducible."],
    ];
    cards.forEach((card, index) => {
      const left = 64 + (index * 390);
      frame(slide, left, 216, 344, 292);
      text(slide, card[0], left + 28, 248, 56, 35, { fontSize: 24, bold: true, color: C.teal });
      text(slide, card[1], left + 28, 314, 254, 32, { fontSize: 24, bold: true });
      text(slide, card[2], left + 28, 374, 274, 82, { fontSize: 16, color: C.muted });
    });
    text(slide, "Alcance: analítica descriptiva y geoespacial. No se declara predicción, riesgo ni causalidad.", 64, 572, 1060, 28, {
      fontSize: 16, bold: true,
    });
    footer(slide, 3);
    notes(slide, "README.md; reports/geospatial/cierre_tecnico.md; reports/ia_exploratoria.md", "El proyecto no presenta el análisis como un modelo predictivo.");
  }

  // 4. Datos
  {
    const slide = deck.slides.add();
    slide.background.fill = C.paper;
    header(slide, "Datos y trazabilidad", "Fuentes oficiales, capas procesadas y controles de integridad", "Los archivos RAW no se modificaron durante el cierre.");
    const values = [
      ["Fuente", "Uso validado", "Resultado"],
      ["Siniestros viales", "Puntos y atributos", "8.332 registros de Comuna 3"],
      ["Malla vial oficial", "Eje Carrera 45", "26 segmentos; 1.698,67 m"],
      ["Límite territorial", "Recorte espacial", "Comuna 3 – Manrique"],
    ];
    const table = slide.tables.add({
      rows: values.length, columns: 3, left: 64, top: 195, width: 700, height: 280,
      values, columnWidths: [190, 255, 255],
    });
    applyTableStyle(table, values.length, 3);
    frame(slide, 808, 195, 408, 282, C.gray);
    text(slide, "Controles congelados", 836, 225, 280, 28, { fontSize: 19, bold: true });
    text(slide, "604", 836, 280, 100, 54, { fontSize: 40, bold: true, color: C.teal });
    text(slide, "IDs oficiales del corredor estricto de 50 m", 956, 293, 215, 44, { fontSize: 14, color: C.muted });
    text(slide, "40 sensibilidad de borde · 4 revisión territorial · 7.684 restantes", 836, 370, 330, 50, { fontSize: 15 });
    text(slide, "No confundir: 644 casos de proximidad simple ≠ 604 siniestros oficiales.", 64, 540, 1030, 28, {
      fontSize: 16, bold: true, color: C.red,
    });
    footer(slide, 4);
    notes(slide, "src/geospatial/ids_cierre_v1.json; reports/geospatial/cierre_tecnico.md", "El cierre distingue explícitamente 604 IDs oficiales de 644 casos de proximidad simple.");
  }

  // 5. Metodología
  {
    const slide = deck.slides.add();
    slide.background.fill = C.gray;
    header(slide, "Metodología", "Un flujo reproducible: cargar → validar → recortar → clasificar → comunicar", "Cada resultado importante conserva evidencia y reglas explícitas.");
    const steps = [
      ["1", "Ingesta", "Siniestros y capas territoriales oficiales."],
      ["2", "Validación", "CRS, geometrías, atributos y calidad de datos."],
      ["3", "Eje vial", "Carrera 45 recortada al límite oficial de Manrique."],
      ["4", "Corredor", "Buffer analítico de 50 m recortado territorialmente."],
      ["5", "Cierre", "Categorías exclusivas, pruebas, dashboard y documentos."],
    ];
    steps.forEach((step, index) => {
      const left = 57 + (index * 239);
      frame(slide, left, 232, 205, 250);
      text(slide, step[0], left + 24, 252, 36, 32, { fontSize: 22, bold: true, color: C.sky });
      text(slide, step[1], left + 24, 314, 158, 30, { fontSize: 18, bold: true });
      text(slide, step[2], left + 24, 367, 156, 72, { fontSize: 13, color: C.muted });
    });
    text(slide, "Criterio analítico: 50 m representa el entorno inmediato del eje; no es una norma de ingeniería vial.", 64, 544, 1080, 32, {
      fontSize: 16, bold: true,
    });
    footer(slide, 5);
    notes(slide, "reports/reporte_corredor_carrera45_50m.txt; reports/geospatial/cierre_tecnico.md", "La metodología preserva geometrías validadas y no rellena gaps artificialmente.");
  }

  // 6. Resultados
  {
    const slide = deck.slides.add();
    slide.background.fill = C.paper;
    header(slide, "Resultados descriptivos", "8.332 siniestros analizados: distribución temporal y resultados del cierre", "Gráfico editable construido con cifras verificadas.");
    frame(slide, 64, 178, 720, 425);
    slide.charts.add("bar", {
      position: { left: 88, top: 200, width: 680, height: 370 },
      title: "Siniestros por año",
      titleTextStyle: { fontSize: 16, bold: true, color: C.ink },
      categories: annual.map((row) => row[0]),
      series: [{ name: "Siniestros", values: annual.map((row) => row[1]), fill: C.teal }],
      hasLegend: false,
      barOptions: { direction: "column", grouping: "clustered", gapWidth: 55 },
      dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 10, color: C.ink } },
      yAxis: { majorGridlines: { style: "solid", fill: C.border, width: 1 } },
    });
    frame(slide, 830, 178, 386, 425, C.gray);
    const metrics = [
      ["604", "corredor estricto"],
      ["40", "sensibilidad de borde"],
      ["4", "revisión territorial"],
      ["439", "celdas de concentración"],
      ["12", "zonas prioritarias exploratorias"],
    ];
    metrics.forEach((metric, index) => {
      const top = 207 + (index * 69);
      text(slide, metric[0], 860, top, 92, 34, { fontSize: 28, bold: true, color: index === 0 ? C.teal : C.ink });
      text(slide, metric[1], 965, top + 7, 200, 28, { fontSize: 14, color: C.muted });
    });
    footer(slide, 6);
    notes(slide, "reports/analisis_espacial_siniestros.md; reports/geospatial/cierre_tecnico.md", "Serie: 2019=1.524; 2020=1.142; 2021=1.413; 2022=1.317; 2023=942; 2024=849; 2025=1.145.");
  }

  // 7. Dashboard
  {
    const slide = deck.slides.add();
    slide.background.fill = C.pale;
    header(slide, "Dashboard web local", "Interfaz verificable para filtros, indicadores y exploración espacial", "Probada localmente en navegador con datos derivados del cierre geoespacial.");
    await image(slide, distanceChart, 64, 182, 568, 343, "Distribución de distancias al eje de Carrera 45", "contain");
    frame(slide, 674, 182, 542, 343);
    text(slide, "Funciones comprobadas", 704, 214, 300, 28, { fontSize: 20, bold: true });
    bullets(slide, [
      "Filtros por año, barrio nominal y clasificación.",
      "Indicadores oficiales: 8.332, 604, 40 y 4.",
      "Gráficas de evolución, gravedad y tipo de siniestro.",
      "Geovisor SVG con zoom, desplazamiento, capas y consulta de zonas.",
    ], 704, 263, 440, 15);
    text(slide, "Evidencia en navegador: HTTP 200; filtros, zoom, capas y consulta de zona verificados.", 64, 558, 1050, 24, {
      fontSize: 15, bold: true,
    });
    footer(slide, 7);
    notes(slide, "web/index.html; web/data/dashboard.json; tests/test_dashboard_geovisor.py", "El gráfico mostrado proviene de reports/distribucion_distancias_siniestros_carrera45.png. La interfaz se verificó en navegador local; la lámina no se presenta como captura.");
  }

  // 8. Geovisor
  {
    const slide = deck.slides.add();
    slide.background.fill = C.paper;
    header(slide, "Geovisor y análisis exploratorio", "Concentraciones, zonas y eje vial como soporte para revisar el territorio", "Las zonas son exploratorias: no equivalen a un índice de riesgo ni a una recomendación causal.");
    await image(slide, qgisMap, 64, 170, 512, 445, "Vista QGIS de concentración, eje y límite territorial", "contain");
    frame(slide, 626, 176, 590, 430, C.gray);
    text(slide, "Lectura responsable de las capas", 656, 208, 390, 30, { fontSize: 20, bold: true });
    bullets(slide, [
      "439 celdas de concentración y 12 zonas prioritarias exploratorias.",
      "El eje definitivo permanece limitado a Manrique; no incorpora territorio de Comuna 4.",
      "Los casos de borde y revisión quedan fuera del indicador principal.",
      "El resultado orienta revisión de campo; no reemplaza estudios de ingeniería.",
    ], 656, 263, 480, 16);
    footer(slide, 8);
    notes(slide, "reports/geospatial/qgis_final_preview.png; reports/geospatial/cierre_tecnico.md", "La vista QGIS es evidencia del análisis exploratorio; no se interpreta como pronóstico o causalidad.");
  }

  // 9. Presupuesto
  {
    const slide = deck.slides.add();
    slide.background.fill = C.gray;
    header(slide, "Propuestas y presupuesto de planeación", "Piloto de seis meses: COP 300.300.000 sin obra física", "Estimaciones de planeación; no son cotizaciones reales.");
    const budget = [
      ["Rubro", "COP"],
      ["Dirección técnica y gestión", "54.000.000"],
      ["Ingeniería de datos y geoespacial", "96.000.000"],
      ["Diseño y visualización", "35.000.000"],
      ["Validación técnica y QA", "22.000.000"],
      ["Trabajo de campo y participación", "48.000.000"],
      ["Infraestructura y licencias", "18.000.000"],
      ["Contingencia", "27.300.000"],
      ["Total estimado sin obra física", "300.300.000"],
    ];
    const table = slide.tables.add({
      rows: budget.length, columns: 2, left: 64, top: 176, width: 680, height: 414,
      values: budget, columnWidths: [485, 195],
    });
    applyTableStyle(table, budget.length, 2, true);
    frame(slide, 792, 177, 424, 411);
    text(slide, "Siguientes validaciones", 822, 211, 280, 30, { fontSize: 20, bold: true });
    bullets(slide, [
      "Validar en campo puntos críticos, velocidad, accesibilidad y cruces.",
      "Priorizar calma de tráfico y seguridad peatonal con población mayor y personas con discapacidad.",
      "Presupuestar intervenciones físicas solo tras diseño, permisos y contratación.",
    ], 822, 267, 340, 16);
    footer(slide, 9);
    notes(slide, "deliverables/presupuesto_estimado.md; reports/recomendaciones_preliminares.md", "La obra física no está incluida. Las recomendaciones requieren validación de campo.");
  }

  // 10. Conclusiones
  {
    const slide = deck.slides.add();
    slide.background.fill = C.ink;
    text(slide, "CIERRE DEL MVP", 64, 62, 250, 24, { fontSize: 13, bold: true, color: "#90D9DF" });
    text(slide, "Una base geoespacial verificable para conversar sobre Carrera 45", 64, 112, 820, 68, {
      fontSize: 34, bold: true, color: C.paper,
    });
    const items = [
      ["Listo para demostrar", "Dashboard local, geovisor, datos íntegros, pruebas y documentos finales."],
      ["Límites explícitos", "No hay modelo predictivo, causalidad, índice de riesgo ni PBIX/PBIP validado."],
      ["Próximo paso responsable", "Validación de campo y revisión institucional antes de decisiones operativas."],
    ];
    items.forEach((item, index) => {
      const top = 249 + (index * 112);
      slide.shapes.add({
        geometry: "roundRect",
        position: { left: 64, top, width: 1115, height: 82 },
        fill: "#173B58",
        line: { style: "solid", fill: "#2C5977", width: 1 },
        borderRadius: "rounded-xl",
      });
      text(slide, item[0], 92, top + 18, 330, 25, { fontSize: 18, bold: true, color: "#90D9DF" });
      text(slide, item[1], 440, top + 17, 680, 43, { fontSize: 14, color: "#E7F3F5" });
    });
    text(slide, "MoviManrique45 · evidencia territorial reproducible para análisis exploratorio", 64, 630, 700, 22, {
      fontSize: 15, color: "#D9E9EE",
    });
    notes(slide, "deliverables/informe_validacion_mvp.md; reports/estado_mvp.md; reports/ia_exploratoria.md", "El MVP está listo para demostración; Power BI e IA/ML mantienen un estado documentado sin sobredeclarar implementación.");
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const name = "slide-" + String(index + 1).padStart(2, "0") + ".png";
    await writeBlob(path.join(PREVIEWS, name), await deck.export({ slide, format: "png", scale: 1 }));
  }

  const modulePath = pathToFileURL(path.join(SKILL, "container_tools", "artifact_tool_utils.mjs")).href;
  const { finalizePresentation } = await import(modulePath);
  const staging = path.join(BUILD, ".codex-finalizer");
  await fs.mkdir(staging, { recursive: true });
  const candidate = path.join(staging, "MoviManrique45_Presentacion_Final_candidate.pptx");
  await (await PresentationFile.exportPptx(deck)).save(candidate);
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
    fontPolicy: { basis: "design", families: [FONT, "Aptos"] },
    verifyArtifactToolImport: true,
    receiptPath: path.join(staging, "MoviManrique45_Presentacion_Final_ajustada.validation.json"),
  });
  console.log(JSON.stringify({ final: FINAL, slides: deck.slides.items.length, validation }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
