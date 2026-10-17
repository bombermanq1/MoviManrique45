# Dashboard web local

Desde la raíz del repositorio, ejecute:

```powershell
.\scripts\iniciar_demo.ps1
```

El iniciador valida los 8.332 eventos, los 604 IDs congelados y las capas de
referencia antes de servir el sitio en `http://127.0.0.1:8501/`. No abra
`index.html` directamente con `file://`: el navegador necesita HTTP para cargar
`data/dashboard.json` y `data/intervenciones.json`.

Los insumos de origen no se versionan. Antes de ejecutar el iniciador, verifique
el paquete local del cierre con `scripts/verificar_insumos_demo.py`; las rutas y
hashes requeridos están en `data/manifest_demo_v1.json`. El servidor se enlaza
solo a `127.0.0.1`.

Para validar solo la exportación derivada, use:

```powershell
.\scripts\iniciar_demo.ps1 -SoloExportar
```

La aplicación no escribe sobre fuentes RAW ni datasets geoespaciales validados.

## Posibles soluciones

La sección **Posibles soluciones en la Carrera 45** muestra las 12 zonas
identificadas. Seleccione una desde el listado, la tabla o el mapa para ver su
ubicación y abrir su ficha. Las fichas presentan registros históricos de la
celda, gravedad y tipos disponibles, relación con el eje cuando existe, lo que
conviene revisar en campo y ocho opciones para evaluar.

Las posibles soluciones comienzan como **Pendiente de inspección**. No
representan obras ejecutadas, prioridades oficiales, costos por zona, causalidad
ni estimaciones de riesgo. Consulte la documentación técnica en
`src/dashboard/README_intervenciones.md`.
