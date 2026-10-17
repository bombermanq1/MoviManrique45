# MoviManrique 45

## Módulo geoespacial

El módulo local automatiza la auditoría de Carrera 45, el análisis de siniestros,
el proyecto QGIS y las exportaciones para Power BI y mapa web.
Consultar [ejecución y metodología](src/geospatial/README.md) y
[resultados y pendientes](reports/geospatial/resumen_implementacion.md).
Los apartados siguientes describen la ingesta inicial del proyecto.

MoviManrique 45 es un proyecto académico y de portafolio orientado a Data Engineering, analítica de datos, movilidad y accesibilidad.

Su propósito es analizar datos de movilidad, accesibilidad y seguridad vial del corredor de la Carrera 45 en la Comuna 3 - Manrique, Medellín.

## Estado actual del MVP

- Dashboard y geovisor local demostrable: consulte [README_DEMO.md](README_DEMO.md).
- Recursos de Power Query, DAX y modelo preparados en `powerbi/implementation/`.
  No existe todavía un archivo PBIX/PBIP validado en Power BI Desktop.
- No se implementa Machine Learning predictivo; el análisis exploratorio se
  documenta explícitamente sin inferir riesgo ni causalidad.

## Tecnologías iniciales

- Python
- Pandas
- Requests

El proyecto no incluye n8n. Power BI cuenta con recursos de implementación,
pero no debe presentarse como un dashboard Power BI funcional hasta validar un
PBIX/PBIP real. Tampoco se presenta el análisis exploratorio como ML funcional.

## Ingesta de siniestros viales

La primera fuente es la capa oficial de siniestralidad de la Secretaría de Movilidad de Medellín. El script `src/ingestion/siniestros.py` consulta el servicio ArcGIS REST mediante paginación, conserva los atributos originales y genera:

- `data/raw/siniestros_medellin.csv`
- `data/processed/siniestros_comuna3.csv`

Para ejecutarlo desde la carpeta raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\ingestion\siniestros.py
```

El script no filtra aún por Carrera 45 ni elimina registros con valores nulos.
