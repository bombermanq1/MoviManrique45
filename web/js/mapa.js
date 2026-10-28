import { CAPAS_CATEGORIA, COLORES, NOMBRES, esc, fmt } from './datos.js';

function recorrerCoordenadas(valor, salida) {
  if (!Array.isArray(valor)) return;
  if (typeof valor[0] === 'number' && typeof valor[1] === 'number') salida.push(valor);
  else valor.forEach(parte => recorrerCoordenadas(parte, salida));
}

function vistaPara(puntos, proporcion, margen = 1.14) {
  const xs = puntos.map(punto => punto[0]);
  const ys = puntos.map(punto => punto[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  let ancho = Math.max(maxX - minX, .001);
  let alto = Math.max(maxY - minY, .001);
  if (ancho / alto < proporcion) ancho = alto * proporcion;
  else alto = ancho / proporcion;
  ancho *= margen;
  alto *= margen;
  return { x: (minX + maxX - ancho) / 2, y: (minY + maxY - alto) / 2, w: ancho, h: alto };
}

export function crearMapa(estado, seleccionarZona) {
  const mapa = document.getElementById('map');
  let anchoSVG = mapa.clientWidth, altoSVG = mapa.clientHeight;
  let vista, vistaBase, arrastre = null, pendiente = false;

  function proyectar(punto) {
    return [(punto[0] - vista.x) / vista.w * anchoSVG, altoSVG - (punto[1] - vista.y) / vista.h * altoSVG];
  }

  function ruta(geometria) {
    const linea = coordenadas => 'M ' + coordenadas.map(punto => proyectar(punto).join(' ')).join(' L ');
    if (geometria.type === 'LineString') return linea(geometria.coordinates);
    if (geometria.type === 'MultiLineString' || geometria.type === 'Polygon') {
      return geometria.coordinates.map(linea).join(' ');
    }
    if (geometria.type === 'MultiPolygon') return geometria.coordinates.flatMap(poligono => poligono.map(linea)).join(' ');
    return '';
  }

  function escalaAproximada() {
    const metrosPorGrado = 111320 * Math.cos((vista.y + vista.h / 2) * Math.PI / 180);
    const objetivo = vista.w * metrosPorGrado / 5;
    const candidatas = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000];
    const metros = candidatas.reduce((mejor, valor) =>
      Math.abs(valor - objetivo) < Math.abs(mejor - objetivo) ? valor : mejor);
    return { metros, pixeles: metros / metrosPorGrado / vista.w * anchoSVG };
  }

  function dibujarMapa() {
    if (!vista) return;
    const capas = Object.fromEntries(Object.entries(CAPAS_CATEGORIA)
      .map(([categoria, id]) => [categoria, document.getElementById(id).checked]));
    const visibles = estado.filtrados.filter(evento => capas[evento.categoria_analisis]);
    const zonaEnFoco = mapa.contains(document.activeElement) ? document.activeElement.dataset.zonaId : null;
    const partes = ['<title>Manrique y el eje de Carrera 45</title>'];
    if (document.getElementById('layer-limite').checked) {
      for (const feature of estado.geo.limite_manrique.features) {
        partes.push(`<path class="limite" d="${ruta(feature.geometry)}" fill="#e2ece1" fill-rule="evenodd" stroke="#819c8e" stroke-width="1.5" vector-effect="non-scaling-stroke"><title>Límite oficial de Manrique</title></path>`);
      }
    }
    if (document.getElementById('layer-zonas').checked) {
      for (const feature of estado.geo.zonas_prioritarias.features) {
        const zona = feature.properties;
        const activa = estado.zonaActiva === zona.zona_id;
        partes.push(`<path class="zona" tabindex="0" role="button" aria-pressed="${activa}" aria-label="Ver zona ${esc(zona.zona_id)}: ${fmt(zona.cantidad)} registros" data-zona-id="${esc(zona.zona_id)}" d="${ruta(feature.geometry)}" fill="${activa ? '#c7b8dc' : '#e3dced'}" fill-rule="evenodd" stroke="#7d65a8" stroke-width="${activa ? 3 : 1.5}"><title>Zona ${esc(zona.zona_id)} · ${fmt(zona.cantidad)} registros históricos</title></path>`);
      }
    }
    for (const evento of visibles) {
      const [x, y] = proyectar([evento.longitud, evento.latitud]);
      const resto = evento.categoria_analisis === 'resto_manrique';
      partes.push(`<circle cx="${x}" cy="${y}" r="${resto ? 1.35 : 3}" fill="${COLORES[evento.categoria_analisis]}" fill-opacity="${resto ? '.35' : '.82'}"><title>Registro ${esc(evento.evento_id)} · ${esc(NOMBRES[evento.categoria_analisis])} · ${esc(evento.anio)}</title></circle>`);
    }
    if (document.getElementById('layer-eje').checked) {
      for (const feature of estado.geo.carrera45.features) {
        partes.push(`<path class="eje" d="${ruta(feature.geometry)}" fill="none" stroke="#087f76" stroke-width="3.5" vector-effect="non-scaling-stroke"><title>Eje Carrera 45 · segmento ${esc(feature.properties.objectid)}</title></path>`);
      }
    }
    const escala = escalaAproximada();
    const baseEscala = altoSVG - 32;
    partes.push(`<g aria-hidden="true"><rect x="12" y="${baseEscala - 14}" width="${Math.max(escala.pixeles + 24, 105)}" height="40" rx="5" fill="#ffffffeb"/><path d="M 24 ${baseEscala} h ${escala.pixeles}" stroke="#36504d" stroke-width="2"/><path d="M 24 ${baseEscala - 4} v 8 M ${24 + escala.pixeles} ${baseEscala - 4} v 8" stroke="#36504d" stroke-width="1.5"/><text x="24" y="${baseEscala + 17}" fill="#36504d" font-size="11">${fmt(escala.metros)} m aprox.</text><path d="M ${anchoSVG - 28} 34 l -6 15 h 12 z" fill="#36504d"/><text x="${anchoSVG - 28}" y="26" text-anchor="middle" fill="#36504d" font-size="12" font-weight="700">N</text></g>`);
    mapa.innerHTML = partes.join('');
    mapa.setAttribute('aria-label', `Mapa con ${fmt(visibles.length)} registros en las capas activas.`);
    document.getElementById('map-status').textContent =
      `${fmt(visibles.length)} registros en las capas activas · ${fmt(estado.filtrados.length)} en la selección.`;
    if (zonaEnFoco) {
      [...mapa.querySelectorAll('[data-zona-id]')].find(elemento => elemento.dataset.zonaId === zonaEnFoco)?.focus({ preventScroll: true });
    }
  }

  function programarMapa() {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(() => { pendiente = false; dibujarMapa(); });
  }

  function actualizarConsultaZona() {
    const zona = estado.geo.zonas_prioritarias.features.find(feature => feature.properties.zona_id === estado.zonaActiva);
    const destino = document.getElementById('zona-consulta');
    destino.innerHTML = zona
      ? `<h3>${esc(zona.properties.zona_id)}</h3><p><strong>${fmt(zona.properties.cantidad)}</strong> registros en el historial completo de la zona.</p>`
      : '<p>Selecciona una zona para consultar su información.</p>';
  }

  function ajustarVista() { vista = { ...vistaBase }; programarMapa(); }

  function enfocar(geometrias, margen) {
    const puntos = [];
    geometrias.forEach(geometria => recorrerCoordenadas(geometria.coordinates, puntos));
    if (puntos.length) { vista = vistaPara(puntos, anchoSVG / altoSVG, margen); programarMapa(); }
  }

  function enfocarZona(id) {
    const zona = estado.geo.zonas_prioritarias.features.find(feature => feature.properties.zona_id === id);
    if (zona) enfocar([zona.geometry], 3);
  }

  function puntoPantalla(evento) {
    // Convierte el puntero a la vista SVG, también después de cambiar el tamaño de pantalla.
    return new DOMPoint(evento.clientX, evento.clientY).matrixTransform(mapa.getScreenCTM().inverse());
  }

  function acercar(factor, punto = { x: anchoSVG / 2, y: altoSVG / 2 }) {
    if (!vista) return;
    const xMapa = vista.x + punto.x / anchoSVG * vista.w;
    const yMapa = vista.y + (1 - punto.y / altoSVG) * vista.h;
    const ancho = Math.max(vistaBase.w * .035, Math.min(vistaBase.w * 4, vista.w * factor));
    const alto = ancho * altoSVG / anchoSVG;
    vista = { x: xMapa - punto.x / anchoSVG * ancho, y: yMapa - (1 - punto.y / altoSVG) * alto, w: ancho, h: alto };
    programarMapa();
  }

  function manejarTeclado(evento) {
    if (!vista) return;
    const paso = vista.w * .1;
    if (evento.key === '+' || evento.key === '=') acercar(.8);
    else if (evento.key === '-') acercar(1.25);
    else if (evento.key === '0') ajustarVista();
    else if (evento.key === 'ArrowLeft') vista.x -= paso;
    else if (evento.key === 'ArrowRight') vista.x += paso;
    else if (evento.key === 'ArrowUp') vista.y += vista.h * .1;
    else if (evento.key === 'ArrowDown') vista.y -= vista.h * .1;
    else if ((evento.key === 'Enter' || evento.key === ' ') && evento.target.dataset.zonaId) {
      seleccionarZona(evento.target.dataset.zonaId);
    } else return;
    evento.preventDefault();
    programarMapa();
  }

  function enlazarMapa() {
    document.getElementById('map-fit').addEventListener('click', ajustarVista);
    document.getElementById('map-road').addEventListener('click', () => enfocar(estado.geo.carrera45.features.map(f => f.geometry), 1.3));
    document.getElementById('map-zoom-in').addEventListener('click', () => acercar(.8));
    document.getElementById('map-zoom-out').addEventListener('click', () => acercar(1.25));
    document.querySelectorAll('[id^="layer-"]').forEach(control => control.addEventListener('change', dibujarMapa));
    mapa.addEventListener('click', evento => {
      const zona = evento.target.closest('[data-zona-id]');
      if (zona) seleccionarZona(zona.dataset.zonaId);
    });
    mapa.addEventListener('keydown', manejarTeclado);
    mapa.addEventListener('wheel', evento => {
      evento.preventDefault();
      acercar(evento.deltaY < 0 ? .82 : 1.22, puntoPantalla(evento));
    }, { passive: false });
    mapa.addEventListener('pointerdown', evento => {
      if (evento.button !== 0 || evento.target.closest('[data-zona-id]')) return;
      arrastre = { id: evento.pointerId, punto: puntoPantalla(evento), vista: { ...vista } };
      mapa.setPointerCapture(evento.pointerId);
      mapa.classList.add('dragging');
    });
    mapa.addEventListener('pointermove', evento => {
      if (!arrastre || arrastre.id !== evento.pointerId) return;
      const punto = puntoPantalla(evento);
      const dx = punto.x - arrastre.punto.x, dy = punto.y - arrastre.punto.y;
      const origen = arrastre.vista;
      vista = { x: origen.x - dx / anchoSVG * origen.w, y: origen.y + dy / altoSVG * origen.h, w: origen.w, h: origen.h };
      programarMapa();
    });
    const terminarArrastre = () => { arrastre = null; mapa.classList.remove('dragging'); };
    for (const nombre of ['pointerup', 'pointercancel', 'lostpointercapture']) mapa.addEventListener(nombre, terminarArrastre);
  }

  const puntos = [];
  [estado.geo.limite_manrique, estado.geo.carrera45, estado.geo.zonas_prioritarias]
    .forEach(capa => capa.features.forEach(feature => recorrerCoordenadas(feature.geometry.coordinates, puntos)));
  estado.base.forEach(evento => puntos.push([evento.longitud, evento.latitud]));
  vistaBase = vistaPara(puntos, anchoSVG / altoSVG);
  vista = { ...vistaBase };
  mapa.setAttribute('viewBox', `0 0 ${anchoSVG} ${altoSVG}`);
  // Ajusta solo el encuadre y los símbolos; conserva intactas las coordenadas de los datos.
  new ResizeObserver(() => {
    if (mapa.clientWidth === anchoSVG && mapa.clientHeight === altoSVG) return;
    const centro = [vista.x + vista.w / 2, vista.y + vista.h / 2];
    const zoom = vista.h / vistaBase.h;
    anchoSVG = mapa.clientWidth;
    altoSVG = mapa.clientHeight;
    vistaBase = vistaPara(puntos, anchoSVG / altoSVG);
    const alto = vistaBase.h * zoom, ancho = alto * anchoSVG / altoSVG;
    vista = { x: centro[0] - ancho / 2, y: centro[1] - alto / 2, w: ancho, h: alto };
    mapa.setAttribute('viewBox', `0 0 ${anchoSVG} ${altoSVG}`);
    programarMapa();
  }).observe(mapa);
  enlazarMapa();
  return { dibujarMapa, actualizarConsultaZona, enfocarZona };
}
