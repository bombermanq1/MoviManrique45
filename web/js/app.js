import { cargarDatos, NOMBRES, conteos, valores, esc, fmt } from './datos.js';
import { crearMapa } from './mapa.js';
import { crearIntervenciones } from './intervenciones.js';

const estado = { geo: null, intervenciones: null, base: [], filtrados: [], zonaActiva: null };
const filtros = ['anio', 'barrio', 'categoria'];
let mapa, intervenciones;

// Navegación disponible incluso cuando los datos aún no han cargado.
function enlazarNavegacion() {
  const toggle = document.getElementById('menu-toggle');
  const menu = document.getElementById('navegacion');
  const cerrar = () => { toggle.setAttribute('aria-expanded', 'false'); menu.classList.remove('is-open'); };
  toggle.addEventListener('click', () => {
    const abierto = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(abierto));
    menu.classList.toggle('is-open', abierto);
  });
  document.querySelectorAll('.topnav a').forEach(enlace => enlace.addEventListener('click', cerrar));
  // Un enlace a una aclaración debe abrir el panel que la contiene, también con URL directa.
  function revelarDestino() {
    const id = location.hash.slice(1);
    if (!id) return;
    const destino = document.getElementById(id);
    if (!destino) return;
    let panel = destino.closest('details');
    while (panel) { panel.open = true; panel = panel.parentElement.closest('details'); }
  }
  window.addEventListener('hashchange', revelarDestino);
  document.querySelectorAll('a[href^="#"]').forEach(enlace => enlace.addEventListener('click', () => {
    if (enlace.hash === location.hash) revelarDestino();
  }));
  revelarDestino();
  document.addEventListener('keydown', evento => {
    if (evento.key === 'Escape') {
      cerrar();
      document.querySelectorAll('.filter[open]').forEach(detalle => { detalle.open = false; });
    }
  });
  const enlaces = [...document.querySelectorAll('.topnav a')];
  const secciones = enlaces.map(enlace => document.querySelector(enlace.hash));
  let navegacionPendiente = false;
  function actualizarSeccionActiva() {
    const visibles = secciones.filter(seccion => seccion.getBoundingClientRect().top <= innerHeight * .35);
    const activa = visibles.at(-1) || secciones[0];
    enlaces.forEach(enlace => {
      if (enlace.hash === '#' + activa.id) enlace.setAttribute('aria-current', 'location');
      else enlace.removeAttribute('aria-current');
    });
    navegacionPendiente = false;
  }
  function programarNavegacion() {
    if (navegacionPendiente) return;
    navegacionPendiente = true;
    requestAnimationFrame(actualizarSeccionActiva);
  }
  window.addEventListener('scroll', programarNavegacion, { passive: true });
  window.addEventListener('resize', programarNavegacion);
  actualizarSeccionActiva();
}

function llenarOpciones(id, opciones) {
  document.getElementById(id).innerHTML = opciones.map(valor =>
    `<option value="${esc(valor)}" selected>${esc(id === 'categoria' ? NOMBRES[valor] : valor)}</option>`).join('');
}

function seleccionados(id) {
  return new Set([...document.getElementById(id).selectedOptions].map(opcion => opcion.value));
}

function resumirFiltros() {
  const todos = { anio: 'Todos los años', barrio: 'Todos los barrios', categoria: 'Todas las categorías' };
  for (const id of filtros) {
    const selector = document.getElementById(id);
    const opciones = [...selector.selectedOptions];
    const texto = opciones.length === selector.options.length ? todos[id]
      : opciones.length === 0 ? 'Ninguno seleccionado'
      : opciones.length === 1 ? opciones[0].textContent
      : opciones.length + ' seleccionados';
    const resumen = document.getElementById(id + '-resumen');
    resumen.textContent = texto;
    resumen.title = texto;
  }
}

function lista(id, objeto) {
  const entradas = Object.entries(objeto).sort((a, b) => b[1] - a[1]);
  const maximo = Math.max(...entradas.map(entrada => entrada[1]), 1);
  document.getElementById(id).innerHTML = entradas.length ? entradas.map(([clave, valor]) =>
    `<li><div class="list-line"><span>${esc(clave)}</span><b>${fmt(valor)}</b></div><span class="distribution-track" aria-hidden="true"><span class="distribution-fill" style="width:${valor / maximo * 100}%"></span></span></li>`).join('')
    : '<li class="empty">No hay registros para esta selección.</li>';
}

function actualizarGraficas(datos) {
  const anual = Object.entries(conteos(datos, 'anio')).sort((a, b) => Number(a[0]) - Number(b[0]));
  const maximo = Math.max(...anual.map(entrada => entrada[1]), 1);
  const destino = document.getElementById('anual');
  destino.innerHTML = anual.length ? anual.map(([anio, cantidad]) =>
    `<div class="bar" style="height:${Math.max(4, cantidad / maximo * 180)}px"><em>${fmt(cantidad)}</em><span>${esc(anio)}</span></div>`).join('')
    : '<p class="empty">No hay registros para esta selección.<br>Ajusta los filtros para volver a ver el gráfico.</p>';
  destino.setAttribute('aria-label', anual.length
    ? 'Siniestros por año: ' + anual.map(([anio, cantidad]) => anio + ', ' + cantidad).join('; ')
    : 'Sin registros para la selección');
  lista('gravedad', conteos(datos, 'gravedad_siniestro'));
  lista('tipo', conteos(datos, 'clase_siniestro'));
}

function renderizar() {
  const anios = seleccionados('anio'), barrios = seleccionados('barrio'), categorias = seleccionados('categoria');
  estado.filtrados = estado.base.filter(evento =>
    anios.has(String(evento.anio)) && barrios.has(String(evento.barrio ?? 'Sin dato')) && categorias.has(evento.categoria_analisis));
  const clasificacion = conteos(estado.filtrados, 'categoria_analisis');
  for (const [id, cantidad] of Object.entries({
    total: estado.filtrados.length,
    principal: clasificacion.principal_50m || 0,
    borde: clasificacion.sensibilidad_borde || 0,
    revision: clasificacion.revision_territorial || 0,
  })) document.getElementById(id).textContent = fmt(cantidad);
  document.getElementById('seleccion-resumen').textContent =
    fmt(estado.filtrados.length) + ' de ' + fmt(estado.base.length) + ' registros · Selección actual';
  resumirFiltros();
  actualizarGraficas(estado.filtrados);
  mapa.dibujarMapa();
}

function restablecerFiltros() {
  document.querySelectorAll('.filters select option').forEach(opcion => { opcion.selected = true; });
  document.querySelectorAll('.filter').forEach(detalle => { detalle.open = false; });
  renderizar();
}

function enlazarFiltros() {
  for (const id of filtros) document.getElementById(id).addEventListener('change', renderizar);
  document.getElementById('restablecer').addEventListener('click', restablecerFiltros);
  document.querySelectorAll('[data-filter]').forEach(boton => boton.addEventListener('click', () => {
    const selector = document.getElementById(boton.dataset.filter);
    [...selector.options].forEach(opcion => { opcion.selected = boton.dataset.select === 'all'; });
    renderizar();
  }));
  document.querySelectorAll('.filter').forEach(detalle => detalle.addEventListener('toggle', () => {
    if (!detalle.open) return;
    document.querySelectorAll('.filter').forEach(otro => { if (otro !== detalle) otro.open = false; });
  }));
  document.addEventListener('click', evento => {
    if (!evento.target.closest('.filter')) document.querySelectorAll('.filter[open]').forEach(detalle => { detalle.open = false; });
  });
}

function seleccionarZona(id) {
  if (!estado.intervenciones.zonas.some(zona => zona.zona_id === id)) return;
  estado.zonaActiva = id;
  mapa.actualizarConsultaZona();
  intervenciones.actualizarFichaIntervenciones();
  mapa.dibujarMapa();
}

function mostrarError(error) {
  document.getElementById('error-detalle').textContent = error.message || String(error);
  document.getElementById('error-carga').hidden = false;
}

async function iniciar() {
  const carga = document.getElementById('carga');
  const reintentar = document.getElementById('reintentar');
  carga.hidden = false;
  reintentar.disabled = true;
  document.getElementById('error-carga').hidden = true;
  document.getElementById('contenido').setAttribute('aria-busy', 'true');
  try {
    const datos = await cargarDatos();
    Object.assign(estado, datos, { base: datos.geo.eventos });
    llenarOpciones('anio', valores(estado.base, 'anio'));
    llenarOpciones('barrio', valores(estado.base, 'barrio'));
    llenarOpciones('categoria', Object.keys(NOMBRES));
    mapa = crearMapa(estado, seleccionarZona);
    intervenciones = crearIntervenciones(estado, seleccionarZona, id => {
      mapa.enfocarZona(id);
      document.getElementById('geovisor').scrollIntoView({ block: 'start' });
    });
    enlazarFiltros();
    seleccionarZona(intervenciones.primeraZona);
    document.getElementById('filtros').disabled = false;
    document.getElementById('capas').disabled = false;
    document.getElementById('zona-selector').disabled = false;
    document.querySelectorAll('.map-toolbar button').forEach(boton => { boton.disabled = false; });
    renderizar();
  } catch (error) {
    mostrarError(error);
  } finally {
    carga.hidden = true;
    reintentar.disabled = false;
    document.getElementById('contenido').setAttribute('aria-busy', 'false');
  }
}

enlazarNavegacion();
document.getElementById('reintentar').addEventListener('click', iniciar);
iniciar();
