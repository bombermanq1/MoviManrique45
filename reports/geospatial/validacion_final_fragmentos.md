# Contraste final local de los seis fragmentos

```text
parte_id  objectid  longitud_m  extremo_inicio_a_vecino_m  extremo_final_a_vecino_m  distancia_al_limite_m  coincide_parte_recorte_raw  hausdorff_recorte_entidad_m  coincide_revision_entidad
  7611:1      7611    0.087723                   0.087723                  0.000000           2.362535e-10                        True                          0.0                       True
 20909:1     20909    0.069021                   0.000000                  0.069021           1.884351e-10                        True                          0.0                       True
 20909:2     20909    0.035759                   0.035759                  0.000000           0.000000e+00                        True                          0.0                       True
 24568:1     24568    0.218238                   0.000000                  0.218238           3.088348e-10                        True                          0.0                       True
 28471:1     28471    0.127048                   0.000000                  0.127048           1.846558e-10                        True                          0.0                       True
 28471:2     28471    0.032631                   0.032631                  0.000000           2.440025e-10                        True                          0.0                       True
```

Se vuelve a intersectar en memoria la entidad correspondiente de la malla RAW con el límite oficial. Se contrasta cada parte diminuta contra ese resultado y la entidad definitiva contra el GeoPackage de revisión. No se guardan geometrías corregidas ni se modifica ninguna fuente.

Advertencia de trazabilidad: la malla RAW declara EPSG:9377, pero sus bounds son [-75.7176274545746, 6.165441495719866, -75.47307943490904, 6.37346201260481]. El script preexistente crear_carrera45_manrique.py documenta su interpretación como EPSG:4326 antes de proyectar. Se reproduce explícitamente esa interpretación solo en memoria para esta comprobación. Confiar literalmente en la etiqueta produciría intersecciones vacías. El inventario inicial verificó la etiqueta, no su coherencia numérica; queda rectificado.

Una parte reproducible por el recorte territorial y tocando su borde es compatible con un efecto del recorte; no demuestra que sea una conexión vial válida ni autoriza eliminarla. Las distancias extremo-a-vecino explican la clasificación conservadora de revisión manual. El contraste con PostgreSQL se registra aparte.
