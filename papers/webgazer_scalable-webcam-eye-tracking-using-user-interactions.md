# webgazer

WebGazer: Scalable Webcam Eye Tracking Using User Interactions

## Introduction

Eyetracking tradicional se hace con equipamiento costos lo cual lo hace
reestrictivo. Los trabajos hechos con webcams domésticas son bastante más
imprecisos. WebGazer busca proveer resultados más precisos utilizando la
interacción del usuario para calibrar continuamente. El modelo de estimación se
va alimentando mientras se recolectan estos mapeos entre miradas y mappings de
eye features.

Soporta diferentes librerías para capturar el bounding box de los ojos. Provee
dos métodos diferentes para estimar la mirada. Difieren en cómo tratan el dato
de los ojos y en el método de regresión. Además de los clicks utiliza
movimientos del cursor y el "gazer-cursor delay" como modificadores. Obtienen
un error promedio de 175 y 210 píxeles respectivamente. El error del ángulo
promedio obtenido es de ~4.17 grados.

## Related work

### webcam eye tracking

- con "sparse calibration" pero se es muy sensible a movimientos de cabeza
- "overcame this using synthetic images for head poses" pero requiere mucha
  calibración
- usar saliency para estimar donde se está mirando, pero es sólo una "rough
  estimate"
- PACE, desktop app que realiza autocalibracion con interacciones del usuario
- TurkerGaze, predice saliency en imágenes

### gazer cursor relationship (en un contexto de web browsing)

- correlación encontra entre "gaze and cursor position"
- retrieval de "relevant parts of the web page" para inferir interés del
  usuario
- se disminuye la distancia cuando se está en una región de interés
- hay fuerte alineamiento, en el eje x la distancia es mayor
- combinación de interacción de usuario y saliency

## Webgazer

No tiene razonamiento 3d. Comentan que es bueno porque permite que webgazer
corra en real time en el navegador. La calibración constante con las
interacciones elimina la necesidad de la calibración inicial y se ajusta a los
movimientos de cabeza del usuario.

Cómo librerías para facial feature detection usan clmtrackr, js-objectdetect y 
tracking.js. Lo que necesitan de este paso es encontrar el rectángulo más chico
que encierre el contorno de los ojos.

Para detectar la pupila asumen:
- el iris es más oscuro que su entorno
- es circular
- la pupila está en el centro

lo cual no es siempre válido. La detección se hace en base a encontrar la región
con mayor contraste.

La posición dos dimensional de la pupila como feature puede fallar. Por eso
hacen como TurkerGaze y usan la alternativa de aprender un mapeo entre píxeles
y gaze location.  "Unlike TurkerGaze, WebGazer does not require users to stare
at calibration points nor remain motionless. It also does not perform offline
post-processing as its goal is live operation instead of image saliency
prediction."

### Mapping to screen and self-calibration

Se necesita construir un mapeo entre 120D y 2D. La relación es compleja pues
depende de la posición 3D de la cabeza y de sus rotaciones. Para aliviar este
problema utilizan en cambio calibración constante.  Exite un delay entre gaze
location y coordenada de la interacción (74 pixeles segun Huang et al, 2012)
pero es task related así que deciden simplifcar el problema y asumir que que la
mirada y el click se alinean perfectamente.

El primer modelo que usan sí se basa en la coordenada de la pupila y es una
regresión lineal directa entre las coordenadas de la pupila y la coordenada en
la pantalla. En el segundo modelo (120D -> 2D) usan ridge regression. No
explican por qué usan distintos modelos, parece que nomás porque es lo que hace
TurkerGaze.

Basándose en que la duración de las fijaciones es de entre 200 y 500ms
mantienen un buffer con todas las features que obtuvieron en los últimos 500ms.
Luego, cuando ocurre un click agregan a la regresión todas las predicciones que
ocurrieron en los últimos 500ms a menos de 72 píxeles del click.

No entiendo si están agregando al modelo sus propias predicciones, asumiendo
que son correctas porque estaban cerca del lugar del click justo antes del
click. "These samples can potentially enrich the accuracy of the predictions
made by the ridge regression." Esto no hay ninguna justificación.

Usan también datos correspondientes al movimiento del mouse durante 200ms luego
del click. El primer click tiene un peso de 1 y el peso de las features
siguientes disminuye 0.05 cada 20ms. Las coordenadas que se alimentan al modelo
son las que predice el mismo modelo.
