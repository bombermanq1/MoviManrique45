export const NOMBRES = {
  principal_50m: 'Dentro del corredor (50 m)',
  sensibilidad_borde: 'Cerca del límite del corredor',
  revision_territorial: 'Ubicación por revisar',
  resto_manrique: 'Otros registros de Manrique',
};
export const COLORES = {
  principal_50m: '#2563c5',
  sensibilidad_borde: '#b97813',
  revision_territorial: '#b34456',
  resto_manrique: '#71818b',
};
export const CAPAS_CATEGORIA = {
  principal_50m: 'layer-principal',
  sensibilidad_borde: 'layer-borde',
  revision_territorial: 'layer-revision',
  resto_manrique: 'layer-resto',
};
const ESPERADO = { principal_50m: 604, sensibilidad_borde: 40, revision_territorial: 4, resto_manrique: 7684 };
const formatoNumero = new Intl.NumberFormat('es-CO');
export const fmt = numero => formatoNumero.format(numero);
export const esc = valor => String(valor ?? '').replace(/[&<>'"]/g, caracter => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
}[caracter]));

export function conteos(datos, campo) {
  return datos.reduce((resultado, fila) => {
    const valor = fila[campo];
    resultado[valor] = (resultado[valor] || 0) + 1;
    return resultado;
  }, {});
}

export function valores(datos, campo) {
  return [...new Set(datos.map(fila => String(fila[campo] ?? 'Sin dato')))]
    .sort((a, b) => a.localeCompare(b, 'es', { numeric: true }));
}

export function validarPayload(geo) {
  if (!Array.isArray(geo?.eventos) || geo.eventos.length !== 8332) {
    throw new Error('La copia de consulta debe contener 8.332 registros.');
  }
  if (new Set(geo.eventos.map(fila => String(fila.evento_id))).size !== 8332) {
    throw new Error('Hay identificadores de siniestros repetidos.');
  }
  const actual = conteos(geo.eventos, 'categoria_analisis');
  if (Object.keys(ESPERADO).some(clave => actual[clave] !== ESPERADO[clave])) {
    throw new Error('Las categorías no coinciden con los datos validados del proyecto.');
  }
  if (geo.limite_manrique?.type !== 'FeatureCollection' || geo.limite_manrique.features.length !== 1) {
    throw new Error('Falta el límite oficial de Manrique.');
  }
  if (geo.carrera45?.features?.length !== 26 || geo.zonas_prioritarias?.features?.length !== 12) {
    throw new Error('Se requieren los 26 segmentos y las 12 zonas del proyecto.');
  }
  if (geo.eventos.some(fila => !Number.isFinite(fila.longitud) || !Number.isFinite(fila.latitud))) {
    throw new Error('Un registro contiene coordenadas que el mapa no puede representar.');
  }
}

export function validarIntervenciones(modulo, geo) {
  if (!Array.isArray(modulo?.zonas) || modulo.zonas.length !== 12) {
    throw new Error('Se requieren las 12 fichas de zonas exploratorias.');
  }
  if (!Array.isArray(modulo.catalogo_intervenciones) || modulo.catalogo_intervenciones.length !== 8) {
    throw new Error('El catálogo de posibles intervenciones está incompleto.');
  }
  if (modulo.metadatos?.eventos_validados !== 8332 || modulo.metadatos?.zonas_exploratorias !== 12) {
    throw new Error('Los metadatos de las fichas no coinciden con los datos validados.');
  }
  const zonasMapa = new Map(geo.zonas_prioritarias.features.map(feature =>
    [String(feature.properties?.zona_id), Number(feature.properties?.cantidad)]));
  const vistos = new Set();
  for (const zona of modulo.zonas) {
    const id = String(zona.zona_id);
    if (vistos.has(id) || !zonasMapa.has(id)) throw new Error('Hay una zona inexistente o repetida.');
    vistos.add(id);
    if (zona.estado_evaluacion !== 'Pendiente de inspección') {
      throw new Error('El estado de una propuesta no coincide con la versión de consulta.');
    }
    if (zona.diagnostico_historico?.registros_historicos !== zonasMapa.get(id)) {
      throw new Error('Los registros de la zona ' + id + ' no coinciden con la capa geográfica.');
    }
  }
  if (vistos.size !== zonasMapa.size) throw new Error('Faltan fichas de zonas.');
}

async function leerJson(ruta) {
  const respuesta = await fetch(ruta);
  if (!respuesta.ok) throw new Error(ruta + ': respuesta HTTP ' + respuesta.status + '.');
  try {
    return await respuesta.json();
  } catch {
    throw new Error(ruta + ' no contiene un JSON válido.');
  }
}

export async function cargarDatos() {
  // Rutas relativas al documento: funcionan también bajo una subcarpeta del sitio.
  const [geo, intervenciones] = await Promise.all([
    leerJson('data/dashboard.json'),
    leerJson('data/intervenciones.json'),
  ]);
  validarPayload(geo);
  validarIntervenciones(intervenciones, geo);
  return { geo, intervenciones };
}
