# Revisión geométrica del eje de Carrera 45

> Evidencia de una ejecución anterior del cierre geoespacial. Se conservan
> sus resultados y tablas; no equivale a una nueva comprobación de PostgreSQL
> ni a las pruebas del frontend. Para el funcionamiento actual, consulta la
> [arquitectura](arquitectura.md).


```text
                indicador       valor
                segmentos   26.000000
                   partes   33.000000
               fragmentos    6.000000
               longitud_m 1698.674535
                invalidas    0.000000
               duplicadas    0.000000
candidatos_discontinuidad   32.000000
```

La revisión conserva las geometrías del eje. Para estudiar sus partes se usa
una capa derivada en EPSG:9377, con distancias en metros.

Tolerancias extremo-a-linea: [0.01, 0.1, 1.0] m. La clasificacion usa 0.01 m; no demuestra conectividad vial funcional. Ambos extremos a esa tolerancia de otra parte: posible conexion valida; invalidez/no simplicidad/longitud cero: posible error; resto: revision manual. Incluye partes del mismo objectid.

```text
parte_id  objectid  parte  longitud_m  diminuta            clasificacion                   decision_version                   origen_documentado
  7611:1      7611      1    0.087723      True Requiere revision manual conservar_sin_eliminar_ni_fusionar reproducible_por_recorte_territorial
 20909:1     20909      1    0.069021      True Requiere revision manual conservar_sin_eliminar_ni_fusionar reproducible_por_recorte_territorial
 20909:2     20909      2    0.035759      True Requiere revision manual conservar_sin_eliminar_ni_fusionar reproducible_por_recorte_territorial
 24568:1     24568      1    0.218238      True Requiere revision manual conservar_sin_eliminar_ni_fusionar reproducible_por_recorte_territorial
 28471:1     28471      1    0.127048      True Requiere revision manual conservar_sin_eliminar_ni_fusionar reproducible_por_recorte_territorial
 28471:2     28471      2    0.032631      True Requiere revision manual conservar_sin_eliminar_ni_fusionar reproducible_por_recorte_territorial
```

```text
extremo_id parte_id  objectid  lado  distancia_vecino_m vecino_parte  conexiones_0_01m  conexiones_0_1m  conexiones_1_0m
  7611:1:0   7611:1      7611     0            0.087723      22535:1                 0                1                1
  7611:1:1   7611:1      7611     1            0.000000      22535:1                 1                1                1
 20909:1:0  20909:1     20909     0            0.000000      20368:1                 1                1                1
 20909:1:1  20909:1     20909     1            0.069021      20368:1                 0                1                1
 20909:2:0  20909:2     20909     0            0.035759      28752:1                 0                1                1
 20909:2:1  20909:2     20909     1            0.000000      28752:1                 1                1                1
 24568:1:0  24568:1     24568     0            0.000000      15098:2                 1                1                1
 24568:1:1  24568:1     24568     1            0.218238      15098:2                 0                0                1
 28471:1:0  28471:1     28471     0            0.000000      22099:1                 1                1                1
 28471:1:1  28471:1     28471     1            0.127048      22099:1                 0                0                1
 28471:2:0  28471:2     28471     0            0.032631       6990:1                 0                1                1
 28471:2:1  28471:2     28471     1            0.000000       6990:1                 1                1                1
```

La capa de discontinuidades representa la separación de cada extremo respecto
a la línea más cercana. Es una ayuda para revisar cortes, ramales o límites
del recorte territorial; no propone rellenar esos espacios. Las relaciones
también registran cruces y solapes entre partes cercanas.

GeoPackage de revision: mismos IDs=True; geometria topologicamente igual en 26/26 entidades.

El reporte anterior de continuidad usa 27 entidades preliminares; este analiza las 26 definitivas. La validacion final previa confirmo coincidencia exacta con PostgreSQL y reproduccion de los seis fragmentos por recorte territorial.

Decision de cierre v1: conservar los seis fragmentos sin eliminar ni fusionar. Reproducibilidad del recorte no demuestra conectividad vial funcional. Ver [contraste](validacion_final_fragmentos.md). Pruebas: relectura exacta de geometria/CRS y conteos. Permanece la revision humana funcional; no la decision de conservacion en esta version.
