# Demostración reproducible de MoviManrique45

El MVP demostrable es el dashboard estático local en `web/`. No requiere
PostgreSQL, servicios externos ni modificación de fuentes RAW. Antes de abrirse,
su exportador valida 8.332 eventos, la unión 1:1 de fecha y coordenadas y los
604 IDs congelados del indicador principal.

## Insumos locales no versionados

Los CSV y capas geográficas validados se excluyen intencionalmente de Git por
contener fuentes y datos locales. Un clon vacío no basta para ejecutar el MVP:
solicite el paquete interno de datos del cierre `v1`, cópielo conservando sus
rutas y valide su integridad antes de iniciar la demo:

```powershell
.\\.venv\\Scripts\\python.exe .\\scripts\\verificar_insumos_demo.py
```

El archivo `data/manifest_demo_v1.json` registra las rutas, tamaños y hashes
SHA-256 esperados. No copie ni publique esos insumos en un repositorio público.

## Preparación inicial

Desde la raíz del repositorio, cree el entorno e instale las dependencias base:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

## Un comando para demostrar el MVP

```powershell
.\\scripts\\iniciar_demo.ps1
```

El comando valida y regenera `web/data/dashboard.json` y
`web/data/intervenciones.json`, después mantiene un servidor local en
`http://127.0.0.1:8501/`. Presione `Ctrl+C` para detenerlo. Si la política de
ejecución local bloquea scripts, use sin cambiar la configuración global:

```powershell
powershell -ExecutionPolicy Bypass -File .\\scripts\\iniciar_demo.ps1
```

El servidor se enlaza exclusivamente a `127.0.0.1`; no se expone a la red
local.

Para validar solamente la exportación, sin abrir un servidor:

```powershell
.\\scripts\\iniciar_demo.ps1 -SoloExportar
```

## Controles de calidad

```powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v
```

Las pruebas cubren el cierre geoespacial, la identidad de los 604 IDs, los
conteos 604/40/4/7.684, la exportación web, los requisitos reproducibles, el
servicio HTTP local y las 12 fichas de intervenciones.

## Posibles soluciones

En el dashboard, abra **Posibles soluciones en la Carrera 45**. Seleccione una
zona desde la lista, la tabla o el mapa. La ficha reúne métricas históricas
verificadas de la celda y opciones sujetas a inspección de campo. El estado
inicial de todas es **Pendiente de inspección** y el costo se mantiene pendiente
de estudio técnico y presupuesto.

## Alternativa Streamlit opcional

`app.py` requiere Streamlit, Plotly y PyDeck. No es necesaria para la
demostración validada anterior. Para prepararla en un entorno con acceso a los
paquetes requeridos:

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -r requirements_mvp.txt
.\\.venv\\Scripts\\streamlit.exe run app.py
```


