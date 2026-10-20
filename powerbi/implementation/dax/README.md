# Medidas DAX copiables

Cada bloque de `medidas_modelo.dax` es una medida independiente. En Power BI
Desktop cree una medida con el mismo nombre y pegue **un bloque a la vez**.

Formato recomendado:

- `Porcentaje corredor sobre Comuna 3`: porcentaje, dos decimales.
- `Mediana distancia corredor m`: decimal, dos decimales y sufijo `m`.
- Conteos: entero con separador de miles.

Las medidas `Registros corredor`, `Registros sensibilidad borde` y
`Registros revisión territorial` eliminan solamente el filtro de clasificación
para fijar la categoría de su tarjeta; conservan filtros temporales, de tipo y
de gravedad. No las use como filas de una matriz por categoría: allí use
`Registros`.

`Integridad IDs principal` debe mostrar `OK — 604 IDs congelados coinciden`
sin filtros. Si muestra ERROR, no publique ni aplique el modelo; revise primero
`ValidacionCierre` y `ControlCierreEstricto` en Power Query.


