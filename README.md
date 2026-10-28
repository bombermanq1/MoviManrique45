# MoviManrique45

MoviManrique45 permite consultar los siniestros de tránsito registrados en
Manrique y explorar su relación espacial con la Carrera 45. Reúne un dashboard,
un geovisor y fichas con posibles intervenciones para revisar en campo.

El proyecto parte de una pregunta concreta: ¿qué muestran los registros
históricos sobre el entorno de esta vía? Para responderla, combina datos
oficiales de siniestros, malla vial y límites territoriales de Medellín. La
aplicación ayuda a consultar esa información; una decisión de intervención
todavía necesita inspección y evaluación técnica.

## Qué puedes consultar

En el dashboard puedes filtrar por año, barrio registrado y ubicación frente
al corredor. Los indicadores, los gráficos y los puntos del mapa responden a
la misma selección. Por ejemplo, puedes consultar los casos de 2025 que
quedaron dentro del corredor, sin mezclarlos con los casos cercanos al límite.

El geovisor muestra el límite de Manrique, el eje de Carrera 45 y las zonas
exploratorias. Puedes activar capas, acercarte al eje y elegir una zona para
consultar su ficha. Cada ficha conserva el historial completo de la celda y
presenta ocho opciones de intervención pendientes de revisión.

La versión actual trabaja con **8.332 siniestros**, **604 casos en el corredor
estricto**, **26 segmentos viales** y **12 zonas exploratorias**. Estas zonas
se identificaron por concentración histórica; no son una clasificación de
riesgo ni representan obras aprobadas.

## Cómo se preparan los datos

Python descarga y procesa las fuentes oficiales. El eje y una franja de
50 metros se recortan al polígono de Manrique. Ese criterio territorial define
los 604 casos del indicador principal. Los registros que requieren revisión
se conservan por separado.

Los resultados llegan al navegador mediante dos JSON locales. La interfaz
consulta esos archivos; no ejecuta el análisis espacial ni escribe en la base
de datos. Los 50 metros son una delimitación analítica del proyecto y no una
norma de ingeniería vial. Las fuentes y reglas completas están en
[datos y metodología](docs/datos.md).

## Ejecutarlo en tu equipo

Desde la raíz del proyecto, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B .\scripts\verificar_insumos_demo.py
.\scripts\iniciar_demo.ps1
```

Abre `http://127.0.0.1:8501/`. El iniciador valida los insumos, regenera los
JSON de consulta y sirve la web. Se detiene con `Ctrl+C`.

Algunos datos no están incluidos en Git. Para regenerar la aplicación necesitas
los archivos indicados en [manifest_demo_v1.json](data/manifest_demo_v1.json).
Si ya tienes ambos JSON exportados y solo quieres consultar la web, puedes
iniciar el servidor sin regenerarlos:

```powershell
.\.venv\Scripts\python.exe -B -m http.server 8501 --bind 127.0.0.1 --directory web
```

Consulta [instalación y pruebas](docs/instalacion.md) si necesitas preparar los
insumos, usar Streamlit o verificar el frontend.

## Organización y tecnologías

```text
README.md       Presentación del proyecto
docs/           Uso, datos, arquitectura y reportes técnicos
web/
  index.html    Estructura de la interfaz
  css/          Estilos y diseño adaptable
  js/           Carga de datos, filtros, mapa y fichas
  data/         JSON que consume el navegador
src/            Ingesta, preparación, análisis y exportación
data/           Fuentes originales y productos procesados
tests/          Pruebas de datos y de la aplicación
scripts/        Comandos de ejecución y verificación
reports/        Evidencias versionadas y salidas locales
powerbi/        Consultas, medidas y archivos de apoyo
qgis/           Proyecto cartográfico
app.py          Interfaz alternativa con Streamlit
```

El procesamiento usa Python, Pandas, GeoPandas, Shapely y Requests. La web está
hecha con HTML, CSS y JavaScript, sin framework ni compilación. Streamlit,
Plotly y PyDeck pertenecen a la interfaz alternativa.

## Estado actual

El dashboard web, sus filtros, el geovisor y las fichas de las 12 zonas están
implementados. También se conserva la aplicación Streamlit; no necesita
ejecutarse para utilizar la web estática.

Power BI tiene consultas M y medidas DAX preparadas, pero no un PBIX/PBIP
validado en Desktop. No hay un modelo predictivo de IA o aprendizaje
automático. Las propuestas de intervención siguen pendientes de inspección,
diseño, presupuesto y autorización.

## Documentación

- [Cómo consultar el dashboard y las zonas](docs/funcionamiento.md).
- [Instalación, despliegue estático y pruebas](docs/instalacion.md).
- [Fuentes y criterios del análisis](docs/datos.md).
- [Arquitectura y cambios en el frontend](docs/arquitectura.md).
- [Campos y categorías de los datos](docs/diccionario_datos.md).
- [Recursos de Power BI](docs/powerbi.md).
