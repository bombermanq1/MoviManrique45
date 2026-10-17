# Manual de ejecución y demostración

## Alcance del MVP local

La demostración validada es el dashboard estático de `web/`. No requiere
PostgreSQL, Internet ni acceso a Power BI Desktop. El iniciador comprueba la
unión 1:1 de fecha/coordenadas, los 8.332 eventos, los conteos por categoría y
los 604 IDs congelados antes de servir la aplicación.

## Preparación inicial

Los datos y capas validados se mantienen fuera de Git. Antes de crear o usar el
entorno, obtenga el paquete interno del cierre `v1` en sus rutas originales y
compruébelo sin modificarlo:

```powershell
.\\.venv\\Scripts\\python.exe .\\scripts\\verificar_insumos_demo.py
```

Consulte `data/manifest_demo_v1.json` para rutas, tamaños y hashes SHA-256. No
publique esos archivos ni los copie a un repositorio público.

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

## Ejecutar y demostrar

Use un único comando:

```powershell
.\\scripts\\iniciar_demo.ps1
```

Abra `http://127.0.0.1:8501/`. El iniciador se enlaza exclusivamente a
`127.0.0.1`, por lo que no publica las ubicaciones históricas en la red local.
Demuestre los filtros de año, barrio y clasificación, las tarjetas, la
evolución anual, la distribución y el geovisor.
El proceso se mantiene activo hasta `Ctrl+C`. Si PowerShell bloquea el script,
ejecútelo sin modificar la política global:

```powershell
powershell -ExecutionPolicy Bypass -File .\\scripts\\iniciar_demo.ps1
```

## Demostrar posibles soluciones

Desplácese a **Posibles soluciones en la Carrera 45**. El selector y el listado
contienen las 12 zonas identificadas. Al elegir una zona desde cualquiera de
esos controles o desde el mapa, el tablero resalta su ubicación y muestra:

- El identificador, ubicación de referencia y registros históricos de la celda.
- Tipos, gravedad y clasificación territorial disponibles.
- Segmentos del eje que intersectan geométricamente la celda, si existen.
- Qué revisar en campo y el catálogo de posibles soluciones.
- Estado **Pendiente de inspección** y costo pendiente de estudio técnico y
  presupuesto.

Explique que el orden comparativo usa solamente el conteo histórico por celda.
No es una tasa de riesgo, una prioridad oficial ni una decisión automática de
obra.

Para comprobar la exportación sin iniciar el servidor:

```powershell
.\\scripts\\iniciar_demo.ps1 -SoloExportar
```

## Ejecutar pruebas

```powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v
```

## Alternativa Streamlit

`app.py` es opcional y no sustituye el dashboard estático validado. Requiere
las dependencias declaradas en `requirements_mvp.txt`:

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -r requirements_mvp.txt
.\\.venv\\Scripts\\streamlit.exe run app.py
```

## Power BI

Use los archivos de `powerbi/implementation/` para crear consultas, relaciones
y medidas. Verifique los conteos en Desktop antes de presentar un dashboard
Power BI como funcional.
