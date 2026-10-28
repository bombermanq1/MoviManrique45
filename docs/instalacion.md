# Instalación y pruebas

Los comandos de esta guía se ejecutan desde la raíz del proyecto, en
PowerShell. La web estática no necesita Node.js, un proceso de compilación ni
PostgreSQL para funcionar.

## Preparar Python y los insumos

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B .\scripts\verificar_insumos_demo.py
```

El último comando compara los archivos locales con
[manifest_demo_v1.json](../data/manifest_demo_v1.json). Algunos insumos están
excluidos de Git: un clon por sí solo no permite regenerar los productos.
Obtén el paquete de datos correspondiente y conserva las rutas del manifiesto.
Si una huella no coincide, revisa el archivo antes de continuar.

## Iniciar la aplicación

```powershell
.\scripts\iniciar_demo.ps1
```

Abre `http://127.0.0.1:8501/`. El iniciador verifica los insumos y genera
`web/data/dashboard.json` e `intervenciones.json` antes de servir la web.
No modifica los RAW. Detén el servidor con `Ctrl+C`.

Si PowerShell bloquea el archivo, puedes permitir su ejecución para ese proceso:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\iniciar_demo.ps1
```

Para exportar sin iniciar el servidor:

```powershell
.\scripts\iniciar_demo.ps1 -SoloExportar
```

Para consultar los JSON existentes sin regenerarlos:

```powershell
.\.venv\Scripts\python.exe -B -m http.server 8501 --bind 127.0.0.1 --directory web
```

No abras `index.html` mediante `file://`: los módulos JavaScript y las
consultas de JSON necesitan HTTP.

## Alojar la web estática

La unidad de despliegue es la carpeta `web/` completa: HTML, CSS, los cuatro
módulos JavaScript, `assets/` y `data/`. No basta con copiar `index.html`. El servidor
debe entregar los archivos `.js` con un tipo MIME de JavaScript.

Las referencias son relativas, por lo que pueden servirse desde la raíz del
sitio o desde una subcarpeta, por ejemplo `/movimanrique45/`. Conserva la barra
final o configura la redirección a ella. El nombre anterior es solo un ejemplo
de ruta; no identifica una publicación real.

Antes de publicar, revisa las condiciones de uso y el detalle de ubicación de
los eventos. No hace falta exponer el repositorio completo, las fuentes RAW ni
credenciales. El servidor de Python descrito aquí es para consulta local.

## Pruebas de Python

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

La suite comprueba identificadores, categorías, geometrías y recursos de la
aplicación. También inicia un servidor temporal para verificar HTML, CSS,
JavaScript y JSON. No requiere escribir en PostgreSQL.

La prueba histórica `test_source_integrity` incluye una ruta externa al
proyecto registrada en `reports/geospatial/run.json`. Si no tienes ese archivo,
la prueba no puede completarse: no cambies las huellas para hacerla pasar.
Las demás pruebas y la verificación de insumos locales se pueden ejecutar
independientemente.

## Pruebas en navegador

[frontend.smoke.cjs](../tests/frontend.smoke.cjs) usa Node.js y Playwright
como herramientas de desarrollo opcionales. La aplicación no los consume.
Con Playwright disponible en el entorno de pruebas y Edge instalado:

```powershell
node .\tests\frontend.smoke.cjs --sin-capturas
```

Si el paquete está instalado fuera del proyecto, puedes indicar su directorio
mediante `PLAYWRIGHT_MODULE`. `PLAYWRIGHT_CHANNEL` permite elegir un canal
compatible; el valor predeterminado es `msedge`.

La prueba inicia su propio servidor temporal y revisa filtros, mapa, fichas,
errores de carga y rutas bajo una subcarpeta. El comando anterior no genera
capturas. Si necesitas evidencia visual, omite `--sin-capturas`: las imágenes
se guardan en `reports/ui/premium/`, una carpeta local excluida de Git.
No ejecuta el ETL ni regenera los datos.

## Interfaz Streamlit

Se conserva como alternativa a la web estática:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements_mvp.txt
.\.venv\Scripts\streamlit.exe run app.py --server.address 127.0.0.1
```

Tiene sus propios controles y visualizaciones con Plotly y PyDeck. El CSS de
`web/` no cambia el aspecto de Streamlit. Ambas interfaces leen productos del
mismo proyecto, pero no comparten estado de filtros.
