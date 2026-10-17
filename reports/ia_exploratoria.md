# Componente exploratorio y alcance de inteligencia artificial

## Estado real

El proyecto no incorpora un modelo predictivo de siniestros. No se implementó uno para evitar atribuir capacidad predictiva a datos sin variables de exposición, flujo vial, velocidad observada, clima, infraestructura detallada o resultados prospectivos.

Esta decisión es deliberada y reproducible: los archivos entregados contienen
eventos históricos, ubicación, fecha, clase, gravedad y clasificación
territorial. No contienen un denominador de exposición por tramo, aforos,
velocidad, inventario homogéneo de infraestructura ni una cohorte futura
independiente para validar una predicción.

## Método disponible

El cierre geoespacial incluye una exploración de concentración histórica mediante una grilla espacial. El resultado contiene 439 celdas y 12 zonas prioritarias exploratorias. Este método es un análisis geoespacial descriptivo, no un modelo de aprendizaje automático y no produce probabilidades de accidente ni tasas de riesgo.

## Variables utilizadas

- Ubicación validada de los siniestros históricos.
- Clasificación territorial del cierre.
- Pertenencia al corredor estricto de 50 m.
- Conteo de eventos por celda.

## Evaluación de viabilidad de aprendizaje automático

| Requisito para un modelo predictivo responsable | Estado con los datos actuales | Consecuencia |
|---|---|---|
| Unidad de exposición comparable por vía, período y población | No disponible | Un conteo no permite estimar una tasa ni comparar riesgo. |
| Variables predictoras observables antes del evento | No disponible de forma sistemática | No se puede entrenar sin fuga de información o variables inventadas. |
| Período futuro separado para validación temporal | No preparado | No se puede medir generalización prospectiva. |
| Definición operacional de objetivo y población en riesgo | Incompleta | No corresponde entrenar un clasificador o regresor. |
| Métricas de desempeño, incertidumbre y sesgo | No aplicables sin el diseño anterior | No se deben publicar predicciones. |

Por estas razones no se incluye `scikit-learn`, clustering presentado como IA ni
un puntaje de riesgo. La ausencia de un modelo no es un fallo de ejecución: es
una salvaguarda metodológica frente a inferencias no sustentadas.

## Interpretación

Las zonas identifican concentración histórica de registros y sirven para priorizar revisión técnica. No establecen causalidad, peligro futuro, desempeño de una intervención ni exposición de la población.

## Evolución propuesta

Una fase futura podría evaluar métodos de agrupamiento espacial o análisis espacio-temporal solo después de incorporar datos de exposición y una estrategia de validación temporal. Cualquier modelo deberá medir desempeño fuera de muestra y comunicar incertidumbre.

Antes de ello se requerirían, como mínimo: aforos o exposición peatonal/vehicular
por tramo y período, velocidad observada, red vial e infraestructura fechadas,
condiciones meteorológicas cuando correspondan, un protocolo de privacidad y una
separación temporal de entrenamiento, validación y prueba. El resultado debería
reportarse como apoyo exploratorio, nunca como causalidad ni como sustituto de la
revisión territorial y de seguridad vial.
