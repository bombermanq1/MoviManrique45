/* Prueba de la interfaz real. No ejecuta el ETL ni modifica datos. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve(__dirname, '..');
const web = path.join(root, 'web');
const snapshots = path.join(root, 'reports', 'ui', 'premium');
const guardarCapturas = !process.argv.includes('--sin-capturas');
const geo = JSON.parse(fs.readFileSync(path.join(web, 'data', 'dashboard.json'), 'utf8'));
const fichas = JSON.parse(fs.readFileSync(path.join(web, 'data', 'intervenciones.json'), 'utf8'));
const results = [];
const record = nombre => { results.push(nombre); console.log('OK ' + nombre); };

const server = http.createServer((req, res) => {
  let pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  if (pathname.startsWith('/movimanrique45/')) pathname = pathname.slice('/movimanrique45'.length);
  const file = path.resolve(web, '.' + pathname, pathname.endsWith('/') ? 'index.html' : '');
  if (!file.startsWith(web + path.sep)) { res.writeHead(403).end(); return; }
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404).end(); return; }
  const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg' };
  res.writeHead(200, { 'Content-Type': (types[path.extname(file)] || 'application/octet-stream') + '; charset=utf-8' });
  fs.createReadStream(file).pipe(res);
});

async function main() {
  if (guardarCapturas) fs.mkdirSync(snapshots, { recursive: true });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({ headless: true, channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const page = await context.newPage();
    const errors = [], failures = [];
    page.on('pageerror', error => { errors.push(error.message); console.error('Error de JavaScript:', error.message); });
    page.on('requestfailed', request => failures.push(request.url()));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text() + ' · ' + message.location().url); });
    async function ready(url = base) {
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.waitForFunction(() => document.querySelector('#total')?.textContent === '8.332');
    }
    async function value(id, expected) {
      assert.equal(await page.locator('#' + id).textContent(), new Intl.NumberFormat('es-CO').format(expected));
    }
    async function filter(id, values) {
      await page.locator('#' + id).locator('..').locator('..').locator('summary').click();
      await page.locator('#' + id).selectOption(values);
    }
    const mapState = () => page.locator('#map .eje').first().getAttribute('d');
    await ready();
    await value('principal', 604); await value('borde', 40); await value('revision', 4);
    assert.equal(await page.locator('#map .eje').count(), 26);
    assert.equal(await page.locator('#map .zona').count(), 12);
    assert.equal(await page.locator('#map circle').count(), 648);
    assert.equal(await page.locator('#anual .bar').count(), 7);
    assert.equal(await page.locator('.hero-image img').evaluate(img => img.complete && img.naturalWidth === 960), true);
    assert.equal(await page.locator('.zone-status, .pending, .limitation-list').count(), 0);
    assert.equal(await page.locator('#alcance-propuestas').getAttribute('open'), null);
    record('Carga de módulos, indicadores, gráficos y capas');

    await filter('anio', ['2025']);
    await value('total', geo.eventos.filter(e => String(e.anio) === '2025').length);
    await filter('categoria', ['principal_50m']);
    await value('principal', geo.eventos.filter(e => String(e.anio) === '2025' && e.categoria_analisis === 'principal_50m').length);
    const barrio = geo.eventos.find(e => e.categoria_analisis === 'principal_50m' && String(e.anio) === '2025').barrio;
    await filter('barrio', [barrio]);
    await value('total', geo.eventos.filter(e => String(e.anio) === '2025' && e.categoria_analisis === 'principal_50m' && e.barrio === barrio).length);
    await page.locator('#restablecer').click();
    await value('total', 8332);
    record('Filtros combinados y restauración');

    await filter('anio', []);
    await value('total', 0);
    assert.equal(await page.locator('#map circle').count(), 0);
    assert.match(await page.locator('#anual').textContent(), /No hay registros/);
    await page.locator('#restablecer').click();
    record('Selección vacía sin datos ficticios');

    await page.locator('#layer-resto').check();
    assert.equal(await page.locator('#map circle').count(), 8332);
    await page.locator('#layer-resto').uncheck();
    await page.locator('#layer-zonas').uncheck();
    assert.equal(await page.locator('#map .zona').count(), 0);
    await page.locator('#layer-zonas').check();
    const beforeZoom = await mapState();
    await page.locator('#map-zoom-in').click();
    await page.waitForFunction(old => document.querySelector('#map .eje').getAttribute('d') !== old, beforeZoom);
    await page.locator('#map').focus();
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('+');
    await page.keyboard.press('0');
    await page.waitForFunction(old => document.querySelector('#map .eje').getAttribute('d') === old, beforeZoom);
    await page.locator('#map-road').click();
    await page.waitForFunction(old => document.querySelector('#map .eje').getAttribute('d') !== old, beforeZoom);
    await page.locator('#map-fit').click();
    await page.waitForFunction(old => document.querySelector('#map .eje').getAttribute('d') === old, beforeZoom);
    record('Capas, zoom, ajuste al eje y teclado');

    await page.locator('#map').scrollIntoViewIfNeeded();
    const box = await page.locator('#map').boundingBox();
    await page.mouse.move(box.x + box.width * .8, box.y + box.height * .4);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * .7, box.y + box.height * .5, { steps: 6 });
    await page.mouse.up();
    await page.waitForFunction(old => document.querySelector('#map .eje').getAttribute('d') !== old, beforeZoom);
    await page.locator('#map-fit').click();
    record('Arrastre del mapa con coordenadas SVG');

    for (const zona of fichas.zonas) {
      await page.locator('#zona-selector').selectOption(zona.zona_id);
      if (await page.locator('#zona-ficha h3').count() === 0) {
        throw new Error('Ficha ausente para ' + zona.zona_id + '; URL: ' + page.url() + '; errores: ' + errors.join('; '));
      }
      assert.match(await page.locator('#zona-ficha h3').textContent(), new RegExp(zona.zona_id));
      assert.equal(await page.locator('#zona-ficha .candidate').count(), 8);
      assert.equal(await page.locator('#zona-ficha .zone-metric strong').first().textContent(), new Intl.NumberFormat('es-CO').format(zona.diagnostico_historico.registros_historicos));
      assert.match(await page.locator('#zona-consulta').textContent(), new RegExp(zona.zona_id));
      assert.match(await page.locator('#zona-ficha .review-status').textContent(), new RegExp(zona.estado_evaluacion));
    }
    await page.locator('#zona-ficha .candidate summary').first().click();
    assert.equal(await page.locator('#zona-ficha .candidate').first().getAttribute('open'), '');
    await page.locator('[data-zone-action="ver-mapa"]').click();
    const firstZone = page.locator('#map .zona').first();
    const firstId = await firstZone.getAttribute('data-zona-id');
    await firstZone.focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#zona-selector').inputValue(), firstId);
    await page.keyboard.press('Space');
    await page.locator('.comparison > summary').click();
    await page.locator('#zona-comparacion button').last().click();
    const lastId = await page.locator('#zona-comparacion button').last().getAttribute('data-zone-selector');
    assert.equal(await page.locator('#zona-selector').inputValue(), lastId);
    record('Las 12 fichas, sus ocho opciones y la selección desde mapa y tabla');

    // Rutas relativas bajo una subcarpeta, como en un alojamiento estático.
    await ready(base + '/movimanrique45/');
    await value('principal', 604);
    for (const asset of ['css/styles.css', 'js/app.js', 'js/datos.js', 'js/mapa.js', 'js/intervenciones.js', 'assets/manrique-constelaciones-2023.jpg']) {
      const response = await page.request.get(base + '/movimanrique45/' + asset);
      assert.equal(response.status(), 200, asset);
    }
    record('Recursos y JSON bajo una subruta de despliegue');

    for (const [name, width, height] of [['escritorio',1440,1000],['portatil',1100,800],['tablet',820,1180],['movil',390,844],['movil_estrecho',320,740]]) {
      await page.setViewportSize({ width, height });
      await page.waitForFunction(() => {
        const map = document.querySelector('#map');
        return map.viewBox.baseVal.width === map.clientWidth && map.viewBox.baseVal.height === map.clientHeight;
      });
      await page.evaluate(() => scrollTo(0, 0));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, name + ': desbordamiento horizontal');
      if (guardarCapturas) {
        await page.screenshot({ path: path.join(snapshots, 'despues_' + name + '.png'), fullPage: true });
        await page.screenshot({ path: path.join(snapshots, 'inicio_' + name + '.png') });
      }
      for (const section of ['resumen', 'geovisor', 'intervenciones']) {
        await page.locator('#' + section).evaluate(element => element.scrollIntoView({ block: 'start' }));
        await page.waitForFunction(id => document.querySelector('.topnav a[aria-current="location"]')?.hash === '#' + id, section);
        if (guardarCapturas) await page.screenshot({ path: path.join(snapshots, section + '_' + name + '.png') });
      }
      if (guardarCapturas) await page.locator('#map').screenshot({ path: path.join(snapshots, 'mapa_' + name + '.png') });
    }
    await page.locator('#menu-toggle').click();
    assert.equal(await page.locator('#menu-toggle').getAttribute('aria-expanded'), 'true');
    await page.locator('.topnav a[href="#geovisor"]').click();
    assert.equal(await page.locator('#menu-toggle').getAttribute('aria-expanded'), 'false');
    record('Escritorio, tablet y móvil sin desbordamiento; menú móvil');

    await page.locator('a[href="#alcance-propuestas"]').click();
    await page.waitForFunction(() => document.querySelector('#alcance-propuestas').open);
    assert.equal(await page.locator('#alcance-propuestas strong').textContent(), 'Pendiente de inspección');
    await page.locator('#alcance-propuestas > summary').click();
    await page.locator('a[href="#alcance-propuestas"]').click();
    await page.waitForFunction(() => document.querySelector('#alcance-propuestas').open);
    await page.locator('#limitaciones > summary').click();
    assert.match(await page.locator('#limitaciones').textContent(), /no demuestra/);
    record('Aclaraciones accesibles sin etiquetas repetidas ni cambio de estado');

    assert.deepEqual(errors, [], 'Errores de consola/JavaScript');
    assert.deepEqual(failures, [], 'Solicitudes fallidas');
    record('Sin errores de JavaScript ni recursos fallidos');

    const errorPage = await context.newPage();
    await errorPage.route('**/data/dashboard.json', route => route.fulfill({ status: 503, body: 'No disponible' }));
    await errorPage.goto(base);
    await errorPage.locator('#error-carga').waitFor({ state: 'visible' });
    assert.equal(await errorPage.locator('#anio').isDisabled(), true);
    assert.equal(await errorPage.locator('#zona-selector').isDisabled(), true);
    await errorPage.unroute('**/data/dashboard.json');
    await errorPage.locator('#reintentar').click();
    await errorPage.waitForFunction(() => document.querySelector('#total').textContent === '8.332');
    assert.equal(await errorPage.locator('#error-carga').isVisible(), false);
    assert.equal(await errorPage.locator('#anio').isDisabled(), false);
    assert.equal(await errorPage.locator('#map .eje').count(), 26);
    assert.equal(await errorPage.locator('#zona-list button').count(), 12);
    record('Error de carga y recuperación sin recargar ni duplicar datos');
    await errorPage.close();
    await context.close();
    console.log(JSON.stringify({ controles: results.length, estado: 'aprobado' }));
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; })
  .finally(() => server.close());
