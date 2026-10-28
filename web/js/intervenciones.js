import { NOMBRES, esc, fmt } from './datos.js';

const ICONOS = {
  pasos_peatonales_seguros: '<path d="M4 5v14M20 5v14M8 7h8M8 11h8M8 15h8M8 19h8"/>',
  reductores_velocidad: '<path d="M3 17h3c1-7 11-7 12 0h3M5 6l2 2M12 3v3M19 6l-2 2"/>',
  senalizacion: '<path d="M12 4v17M4 6h12l4 4-4 4H4z"/>',
  accesibilidad_universal: '<circle cx="12" cy="4" r="2"/><path d="M5 8h14M12 7v7M12 14l-5 7M12 14l5 7"/>',
  rampas_cruces: '<path d="M3 20h18M4 16h5v-4h5V8h6M4 8l15-5"/>',
  control_velocidad: '<path d="M4 18a9 9 0 1 1 16 0M12 13l5-5M5 13h2M12 4v2M17 13h2"/><circle cx="12" cy="13" r="1.5"/>',
  proteccion_peatones_transporte: '<rect x="5" y="3" width="14" height="16" rx="3"/><path d="M5 11h14M8 19v2M16 19v2"/><circle cx="8" cy="15" r="1"/><circle cx="16" cy="15" r="1"/>',
  visibilidad_espacio_peatonal: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
};
const TITULOS_MEDIDAS = {
  senalizacion: 'Señales y demarcación',
  accesibilidad_universal: 'Accesibilidad universal',
  rampas_cruces: 'Rampas y cruces',
  control_velocidad: 'Control de velocidad',
  proteccion_peatones_transporte: 'Peatones y transporte',
  visibilidad_espacio_peatonal: 'Visibilidad y espacio peatonal',
};


function listaDeConteos(items, categorias = false) {
  if (!items?.length) return '<p class="note">Sin datos registrados.</p>';
  return `<ul class="compact-list">${items.map(item =>
    `<li><span>${esc(categorias ? NOMBRES[item.valor] || item.valor : item.valor)}</span><b>${fmt(item.cantidad)}</b></li>`).join('')}</ul>`;
}

function tarjetaMedida(medida) {
  return `<details class="candidate">
    <summary><span class="candidate-icon" aria-hidden="true"><svg viewBox="0 0 24 24">${ICONOS[medida.id] || '<circle cx="12" cy="12" r="8"/>'}</svg></span><span>${esc(TITULOS_MEDIDAS[medida.id] || medida.nombre)}</span></summary>
    <div class="candidate-body">
      <p>${esc(medida.descripcion)}</p>
      <p><strong>Qué podría atender:</strong> ${esc(medida.problema_atendido)}</p>
      <p><strong>Qué se espera mejorar:</strong> ${esc(medida.beneficio_hipotesis)}</p>
      <p><strong>Qué habría que verificar:</strong> ${esc(medida.condiciones_necesarias)}</p>
      <p><strong>Quién debe evaluarlo:</strong> ${esc(medida.entidad_evaluadora)}</p>
      <p><strong>Inspección de campo:</strong> ${medida.requiere_inspeccion_campo ? 'requerida' : 'por definir'}.</p>
    </div>
  </details>`;
}

export function crearIntervenciones(estado, seleccionarZona, verEnMapa) {
  const modulo = estado.intervenciones;
  const porId = new Map(modulo.zonas.map(zona => [zona.zona_id, zona]));
  const catalogo = new Map(modulo.catalogo_intervenciones.map(medida => [medida.id, medida]));
  const zonas = [...modulo.zonas].sort((a, b) =>
    a.comparacion_exploratoria.orden_por_registros_historicos - b.comparacion_exploratoria.orden_por_registros_historicos);
  const selector = document.getElementById('zona-selector');

  function fichaDeZona(zona) {
    const historico = zona.diagnostico_historico;
    const evidencia = zona.evidencia_geoespacial;
    const centro = zona.ubicacion.centroide_representativo_wgs84;
    const barrios = historico.barrios_nominales_observados.map(item => esc(item.valor)).join(' · ');
    const segmentos = evidencia.segmentos_eje_intersectados_objectid.length
      ? evidencia.segmentos_eje_intersectados_objectid.map(esc).join(', ')
      : 'Ningún segmento del eje cruza esta celda.';
    const tarjetas = zona.intervenciones_candidatas.map(id => catalogo.get(id)).filter(Boolean).map(tarjetaMedida).join('');
    return `
      <div class="zone-heading">
        <div><p class="eyebrow">Zona exploratoria · ${esc(historico.periodo.inicio)}–${esc(historico.periodo.fin)}</p><h3>Zona ${esc(zona.zona_id)}</h3><p class="zone-location">${barrios || 'Barrio sin dato'}</p></div>
        <button class="button" type="button" data-zone-action="ver-mapa">Ver en el mapa ↗</button>
      </div>
      <div class="zone-metrics">
        <article class="zone-metric"><span>Registros históricos</span><strong>${fmt(historico.registros_historicos)}</strong></article>
        <article class="zone-metric"><span>En el corredor de 50 m</span><strong>${fmt(historico.corredor_estricto_50m)}</strong></article>
        <article class="zone-metric"><span>Orden por registros</span><strong>#${fmt(zona.comparacion_exploratoria.orden_por_registros_historicos)}</strong></article>
      </div>
      <section class="zone-review" aria-label="Posibles soluciones para la zona">
        <h4>Posibles mejoras para estudiar</h4>
        <p class="note">Ocho alternativas. Abre una para conocer su propósito y sus condiciones.</p>
        <div class="candidate-grid">${tarjetas}</div>
      </section>
      <details class="technical-detail">
        <summary>Ver el historial de la zona</summary>
        <div class="evidence-grid">
          <section class="evidence-block"><h4>Gravedad registrada</h4>${listaDeConteos(historico.por_gravedad)}<h4>Tipo de siniestro</h4>${listaDeConteos(historico.por_tipo)}</section>
          <section class="evidence-block"><h4>Ubicación frente al corredor</h4>${listaDeConteos(historico.por_categoria_analisis, true)}<h4>Barrios registrados</h4>${listaDeConteos(historico.barrios_nominales_observados)}</section>
        </div>
      </details>
      <details class="technical-detail">
        <summary>Ubicación y criterio de selección</summary>
        <p class="note">Punto de referencia de la celda: ${Number(centro.latitud).toFixed(6)}, ${Number(centro.longitud).toFixed(6)}. No corresponde a una obra.</p>
        <p class="note"><strong>Segmentos del eje:</strong> ${segmentos}</p>
        <p class="note">${esc(evidencia.mensaje_segmento)}</p>
        <p class="note">${esc(zona.justificacion)}</p>
        <p class="note">${esc(zona.comparacion_exploratoria.criterio)} ${esc(zona.comparacion_exploratoria.aclaracion)}</p>
      </details>
      <details class="technical-detail">
        <summary>Qué verificar antes de intervenir</summary>
        <p class="review-status"><strong>Estado de la zona:</strong> ${esc(zona.estado_evaluacion)}.</p>
        <ul class="field-checks">${zona.condiciones_por_verificar.map(item => `<li>${esc(item)}</li>`).join('')}</ul>
        <p class="cost-note"><strong>${esc(zona.costos_preliminares.estado)}</strong><br>${esc(zona.costos_preliminares.nota)}</p>
      </details>
    `;
  }

  function actualizarFichaIntervenciones() {
    const zona = porId.get(estado.zonaActiva);
    if (!zona) return;
    selector.value = zona.zona_id;
    document.querySelectorAll('[data-zone-selector]').forEach(boton =>
      boton.setAttribute('aria-current', String(boton.dataset.zoneSelector === zona.zona_id)));
    document.getElementById('zona-ficha').innerHTML = fichaDeZona(zona);
  }

  selector.innerHTML = zonas.map(zona => `<option value="${esc(zona.zona_id)}">${esc(zona.zona_id)} · ${fmt(zona.diagnostico_historico.registros_historicos)} registros</option>`).join('');
  document.getElementById('zona-list').innerHTML = zonas.map(zona =>
    `<li><button type="button" data-zone-selector="${esc(zona.zona_id)}"><span><small>${fmt(zona.comparacion_exploratoria.orden_por_registros_historicos).padStart(2, '0')}</small>${esc(zona.zona_id)}</span><b>${fmt(zona.diagnostico_historico.registros_historicos)}</b></button></li>`).join('');
  document.getElementById('zona-comparacion').innerHTML = zonas.map(zona =>
    `<tr><td>${fmt(zona.comparacion_exploratoria.orden_por_registros_historicos)}</td><td>${esc(zona.zona_id)}</td><td>${fmt(zona.diagnostico_historico.registros_historicos)}</td><td>${fmt(zona.diagnostico_historico.corredor_estricto_50m)}</td><td><button type="button" data-zone-selector="${esc(zona.zona_id)}">Ver zona</button></td></tr>`).join('');
  document.getElementById('intervenciones-limitaciones').innerHTML = modulo.limitaciones_modulo.map(item => `<li>${esc(item)}</li>`).join('');

  selector.addEventListener('change', evento => seleccionarZona(evento.target.value));
  for (const id of ['zona-list', 'zona-comparacion']) {
    document.getElementById(id).addEventListener('click', evento => {
      const boton = evento.target.closest('[data-zone-selector]');
      if (!boton) return;
      seleccionarZona(boton.dataset.zoneSelector);
      if (id === 'zona-comparacion') {
        document.getElementById('zona-ficha').scrollIntoView({ block: 'start' });
      }
    });
  }
  document.getElementById('zona-ficha').addEventListener('click', evento => {
    if (evento.target.closest('[data-zone-action="ver-mapa"]')) verEnMapa(estado.zonaActiva);
  });
  return { actualizarFichaIntervenciones, primeraZona: zonas[0].zona_id };
}
