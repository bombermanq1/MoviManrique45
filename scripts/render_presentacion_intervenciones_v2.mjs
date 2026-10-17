/** Renderiza para control visual la presentación final seleccionada por estilo. */
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "C:\\Users\\matth\\OneDrive\\Escritorio\\ITM\\movimanrique45";
const ES_V3 = (process.env.MOVIMANRIQUE_ESTILO || "v2").trim().toLowerCase() === "v3";
const ETIQUETA_ARCHIVO = ES_V3 ? "v3_Textos_Claros" : "v2_Intervenciones";
const NODE_MODULES = "C:\\Users\\matth\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const ARTIFACT = path.join(NODE_MODULES, "@oai", "artifact-tool", "dist", "artifact_tool.mjs");
const INPUT = path.join(ROOT, "deliverables", "final", ES_V3 ? "v3_textos_claros" : "v2", `MoviManrique45_Presentacion_${ETIQUETA_ARCHIVO}.pptx`);
const OUTPUT = path.join(ROOT, ".build", ES_V3 ? "presentacion_textos_claros_v3" : "presentacion_intervenciones_v2", "final_previews");
const { FileBlob, PresentationFile } = await import(pathToFileURL(ARTIFACT).href);

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

const presentation = await PresentationFile.importPptx(await FileBlob.load(INPUT));
for (const [index, slide] of presentation.slides.items.entries()) {
  const output = path.join(OUTPUT, `slide-${String(index + 1).padStart(2, "0")}.png`);
  await writeBlob(output, await presentation.export({ slide, format: "png", scale: 1 }));
}
console.log(`Renderizadas ${presentation.slides.items.length} diapositivas en ${OUTPUT}`);
