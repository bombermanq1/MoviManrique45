# Informe de validación del MVP

## Última ejecución verificable

- Fecha: 16 de octubre de 2026.
- Comando: `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v`.
- Resultado: **50 pruebas ejecutadas, 50 aprobadas, 0 fallos**.
- Duración observada: **2,884 segundos**.

La ejecución se realizó desde la raíz del repositorio y sobre las fuentes y
productos locales existentes. No se usó PostgreSQL ni se modificaron fuentes
RAW, capas oficiales, IDs congelados ni geometrías validadas.

## Cobertura ejecutada

| Grupo | Pruebas | Controles principales |
|---|---:|---|
| Cierre geoespacial | 30 | Conteos, IDs congelados, CRS, 26 segmentos, 33 partes, seis fragmentos, integridad de fuentes y capas. |
| Dashboard y geovisor | 6 | Unión 1:1, IDs congelados de las tres categorías, límite oficial de Manrique, contrato de capas e interacciones declaradas. |
| Intervenciones exploratorias | 6 | Doce fichas reales, métricas conciliadas con los eventos, ocho medidas candidatas, estado pendiente, intersecciones reales y contrato HTML. |
| Entregables MVP | 2 | Presencia de insumos y conservación del total en la exportación web. |
| Reproducibilidad web | 4 | Requisitos UTF-8, iniciador, conteos publicados y respuesta HTTP local para ambos JSON. |
| Seguridad PostgreSQL | 2 | Los módulos no solicitan credenciales al importarse y la escritura exige una bandera explícita. |
| **Total** | **50** | **Suite completa aprobada.** |

## Controles verificados

- 8.332 eventos e IDs únicos.
- Partición excluyente de 604, 40, 4 y 7.684 eventos.
- Identidad exacta de los IDs congelados principal, de borde y de revisión.
- Unión 1:1 de fecha, latitud y longitud.
- Conservación de los seis fragmentos y de la discrepancia CRS documentada.
- Límite territorial oficial de Manrique, eje de 26 segmentos y 12 zonas
  prioritarias exploratorias en el contrato web.
- Doce fichas de intervención derivadas de los eventos y geometrías reales,
  con estado uniforme `Pendiente de inspección` y sin costos por zona inventados.
- Respuesta HTTP 200 para la página, `dashboard.json` e `intervenciones.json`
  del dashboard local.
- Declaración de las dependencias base y opcionales de Streamlit/PyDeck, además
  del iniciador `scripts/iniciar_demo.ps1`.
- Validación SHA-256 de los insumos no versionados requeridos para el MVP y
  servidor de demostración limitado a `127.0.0.1`.

## Comprobaciones adicionales de entorno

- `python -m pip check`: sin dependencias rotas en el entorno local.
- Escaneo de secretos literales en archivos de texto relevantes: sin
  coincidencias.
- La alternativa Streamlit sigue siendo opcional: sus paquetes no estaban
  instalados en este entorno durante esta validación. El dashboard estático
  validado no depende de ellos.

## Limitaciones

Power BI Desktop no se validó en esta ejecución y no se afirma que exista un
PBIX/PBIP funcional a partir de esta evidencia. El tablero describe datos
históricos; no estima riesgo, exposición ni causalidad.
