## Entregables preparados

| Recurso | Uso |
|---|---|
| [powerquery/README.md](powerquery/README.md) | Orden exacto para crear consultas M independientes |
| [powerquery/](powerquery) | Funciones, staging, dimensiones, hechos y controles de cierre |
| [dax/medidas_modelo.dax](dax/medidas_modelo.dax) | Medidas DAX copiables, incluida integridad exacta de los 604 IDs |
| [modelo_relaciones.md](modelo_relaciones.md) | Modelo estrella, nueve relaciones y configuración semántica |
| [guia_4_paginas.md](guia_4_paginas.md) | Procedimiento y aceptación de Resumen, Carrera 45, Geográfico y Calidad |
| [validar_recursos_powerbi.py](validar_recursos_powerbi.py) | Validación estática reproducible de datos y recursos |
| [estado_pbip.md](estado_pbip.md) | Bloqueo exacto de PBIX/PBIP y procedimiento para completarlo en Desktop |

`consultas_powerquery.m` ahora es un índice válido y no un bloque de varias
consultas concatenadas. `medidas.dax` se conserva como una versión compacta
histórica; el archivo canónico para la implementación es
`dax/medidas_modelo.dax`.

## Ejecución de validación estática

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe powerbi\implementation\validar_recursos_powerbi.py
```

El script produce `validacion_estatica_powerbi.md` y `.json` dentro de esta
carpeta. Comprueba datos, los IDs congelados, fuentes permitidas, presencia de
recursos M/DAX y balance básico de paréntesis DAX. No compila M/DAX ni prueba
Power BI Desktop; esos resultados solo pueden confirmarse al abrir el modelo.

## Estado real

- Consultas, modelo, medidas, relaciones, validación 604 y las cuatro guías de
  página: **preparados para importación manual**.
- PBIX/PBIP: **no generado ni validado**. Consulte
  [estado_pbip.md](estado_pbip.md); no se fabrica un artefacto que no pueda
  abrirse y refrescarse en Desktop.
- Publicación, PostgreSQL y conexiones externas: **no usados**.
