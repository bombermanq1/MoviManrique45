# Consultar la aplicación

Abre el dashboard mediante un servidor HTTP. Los comandos están en
[instalación](instalacion.md). El menú lleva a **Inicio**, **Los datos**,
**Geovisor**, **Las zonas** y **Metodología**; en móvil se despliega con el
botón **Menú**.

## Leer los resultados

Las cuatro tarjetas muestran los registros seleccionados, los casos dentro del
corredor estricto, los cercanos al límite y las ubicaciones por revisar. Sus
valores cambian con los filtros. Las cifras de la portada —8.332 registros,
604 del corredor estricto, 26 segmentos y 12 zonas— describen el conjunto
completo del proyecto y no cambian al filtrar.

Abre un filtro para elegir años, barrios o categorías. Puedes seleccionar
varios valores con Ctrl/Cmd o Mayús, o usar los controles **Todos** y
**Ninguno**. Por ejemplo, al elegir 2025 y «Dentro del corredor (50 m)», los
gráficos muestran únicamente los registros que cumplen ambas condiciones.
**Limpiar filtros** devuelve la selección completa.

Una selección sin coincidencias muestra cero registros y un mensaje en el
gráfico. No se reemplazan los resultados por un ejemplo ni por datos de otro
periodo.

## Explorar el mapa

El mapa representa las capas del proyecto sin un mapa base externo. Permite:

- Acercarse a la Carrera 45 con **Acercar al eje** y recuperar la vista general
  con **Ver todo**.
- Desplazarse arrastrando y cambiar el zoom con la rueda o los botones.
- Mostrar u ocultar capas y seleccionar una zona para consultar sus datos.

Con el mapa enfocado, las flechas desplazan la vista, + y − cambian el zoom y
0 recupera la vista general. Una zona enfocada se selecciona con Enter o
espacio. En móvil se puede arrastrar y utilizar los botones de zoom.

Los filtros deciden qué registros se consultan; las capas deciden cuáles se
dibujan. El conteo de las capas activas puede ser menor que el total
seleccionado; no cambia al acercar o desplazar la vista. La capa «Otros
registros» comienza apagada para facilitar la lectura del corredor.

## Consultar las zonas y las propuestas

Selecciona una zona desde el mapa, el selector, el listado lateral o la tabla
**Comparar las 12 zonas**. La ficha muestra su historial, los segmentos del
eje que la intersectan y las condiciones que habría que revisar en terreno.
**Ver en el mapa** acerca la vista a la celda seleccionada.

Las fichas usan el historial completo de cada zona. No se recalculan al filtrar
el dashboard por año o barrio. El orden del listado corresponde al número de
registros históricos, no a una puntuación de riesgo.

Cada ficha presenta primero ocho opciones del catálogo. Abre una para conocer
su propósito, las condiciones que necesita y la entidad que debería evaluarla.
El historial, el criterio de selección y las verificaciones de campo están
en paneles desplegables debajo de las opciones.

En **Qué verificar antes de intervenir** se conserva el estado **Pendiente de
inspección** y la aclaración sobre los costos. La presencia de una propuesta
en la ficha no acredita una inspección ni una obra ejecutada.

## Interpretar los datos

Los gráficos cuentan registros de siniestros, no víctimas. Las diferencias
entre años pueden depender de la cobertura del reporte. Para entender los
604 casos estrictos, la sensibilidad al borde y las limitaciones del análisis,
consulta [datos y metodología](datos.md).

La sección **Metodología** de la web reúne las aclaraciones en cuatro paneles
desplegables. El enlace **Cómo leer estas propuestas** abre directamente su
panel. La sección también explica por qué los 50 m son una decisión analítica
y qué falta por verificar en terreno.

Si falla la carga, la aplicación muestra el problema y deja deshabilitados
los controles de datos. **Volver a intentar** repite la consulta de los JSON.
La metodología y la navegación siguen disponibles.
