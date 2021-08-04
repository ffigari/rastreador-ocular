# rastreador-ocular

## Implementación

Con `./install.sh` se instalan las dependencias.  
El entry point es `index.html`.
Se puede hacer `firefox index.html` por ejemplo.

## Notas

Estimación de mirada en experimentos en navegador y sin interacción continua
por parte del usuario.

### Trabajo relacionado

Puipl ext como libería que busca estandarizar cómo se mide la pupila.

Webgazer como librería que corre en el navegador. Toma muchas ideas de
TurkerGaze. En lugar de centrarse en una calibración inicial buscan calibrar a
medida que el usuario interactúa con la página web. No utilizan ningún modelado
3D. Simplifican el problema asumiendo que el lugar del click se corresponde
exactamente al lugar de la mirada. No me queda claro como alimentan al modelo
cuando ocurre algún click. Creo que hacen algo similar a agregar las features
capturadas en los 500ms anteriores, pero no entiendo a qué posición mapean esas
features (el ojo, o la predicción que estaban realizando?). Tampoco me queda
aclaran si van descartando datos viejos o si los mantienen dentro del modelo.

#### apuntes de los leídos:

- [
  [1] PupilEXT: Flexible Open-Source Platform for High-Resolution Pupillometry in Vision Research
](
  /papers/pupilext-flexible-open-source-platform-for-high-resolution-pupillometry-in-vision-research.md
)
- [
  [2] WebGazer: Scalable Webcam Eye Tracking Using User Interactions
](
  /papers/webgazer_scalable-webcam-eye-tracking-using-user-interactions.md
)

### otros que podría ser interestante leer, en ningún orden particular:

- Dan Witzner Hansen and Qiang Ji. In the eye of the beholder: A survey of models for eyes and gaze. IEEE TPAMI, 32(3):478—500, 2010.
- Zhang, Z. (2000). A flexible new technique for camera calibration. IEEE Trans. Pattern Anal. Mach. Intell. 22, 1330–1334. doi: 10.1109/34.888718
- Holmqvist, K., Nyström, M., and Mulvey, F. (2012). “Eye tracker data quality: what it is and how to measure it,” in Proceedings of the Symposium on Eye Tracking Research and Applications ETRA ‘12, (New York, NY: ACM Press), 45. doi: 10.1145/2168556.2168563
- Arvin, S., Rasmussen, R., and Yonehara, K. (2020). EyeLoop: an open-source, high-speed eye-tracker designed for dynamic experiments. bioRxiv [Preprint]. doi: 10.1101/2020.07.03.186387
- Santini, T., Fuhl, W., Geisler, D., and Kasneci, E. (2017). “EyeRecToo: open-source software for real-time pervasive head-mounted eye tracking,” in VISIGRAPP 2017 Proceedings of the 12th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications, (Setúbal: SciTePress), 96–101. doi: 10.5220/0006224700960101
- Santini, T., Fuhl, W., and Kasneci, E. (2018a). PuRe: robust pupil detection for real-time pervasive eye tracking. Comput. Vis. Image Underst. 170, 40–50. doi: 10.1016/j.cviu.2018.02.002

### Variables

#### Algoritmo de calibración

- Cuándo?
Se recalibra cada cierto tiempo, cada cierta cantidad de experimentos, cuando
se detecta drifting?
- Cómo?
Mostrando estímulos controlados a los cuales el usuario debe mirar
explícitamente?
De manera implícita en base a las interacciones del usuario con el navegador?

#### Entorno experimental remoto no controlado

La luminosidad es variable.
Puede incluso variar dentro de un mismo expermiento.

No hay un técnico que indique al usuario cómo posicionar la cámara, la cabeza.
En un laboratorio es más fácil garantizar que por ejemplo el sujeto no se
reacomode, que no aleje / acerque la cabeza, que la incline.

#### Basado en webcam de notebook

Los eye trackers tradicionales (los basados en equipamiento especializado)
suelen usar cámaras infrarrojas que son menos afectadas por los cambios de luz.

[
  buscar las fichas técnicas de eye trackers comerciales
  confirmar esto de las cámaras infrarrojas
]

Otra diferencia es la posición de la cámara, en particular la altura del lente.
En un labo la cámara suele posicionarse a la altura de los ojos, mientras que la
notebook puede estar sobre las piernas del usuario, sobre una mesa.
Puede andar sentado en una cama, sobre un escritorio.
Cómo afecta el ángulo de la cámara? Puede detectarse ese ángulo?

### Experimentación

#### Cómo medir la calidad de los resultados?

Lo que tengo en la cabeza es armar un programa que:
- calibra
- muestra unos estímulos controlados
- mide que tan bien anduvo la calibracón.

Para la calibración voy a estar usando la que provee jspsych-webgazer
Los estímulos van a ser nomás unos puntos similares a los que muestra esa
calibración.  
Lo que no me queda muy claro es qué data caṕturar durante el experimento.
Seguro voy a guardar la coordenada del estímulo que se muestra y la predicción
del eye tracker.

Lo que no me queda muy claro es si guardar cosas del entorno y de la calibración
y en tal caso qué cosas guardar.
Si quiero entender como esos dos grupos de variables influencian las
predicciones entonces sí tengo que guardar datos relacionados.

Una variable sencillamente guardable es el input de la webcam.
Guardar un video entero del experimento capaz es muy caro, tanto en poder de
cómputo (hace que ande todo más lento) como en storage (dónde guardo todo ese
video).
Capaz alcanza con una captura del inicio del exprimento, pero en ese caso no
podría analizar como afectan los cambios en el posicionamiento del sujeto
relativo a la cámara.

Hay algunas variables como la distancia del sujeto a la cámara o el ángulo entre
el lente y los ojos que capaz puedan calcularse pero no parece sencillo.
Para estas cosas tendría que explorar un poco la bibliografía y en particular la
metodología que utilizan para comparar distintas implementaciones o
equipamientos.

Dsp cosas como si el sujeto tiene la notebook en una mesa o sobre las piernas o
el ángulo con el cual está abierta la notebook ya tendría que anotarlas más a
mano.

Tampoco es evidente el nivel de complejidad que tenga sentido darle al
experimento.
Quisiera tener un dataset del estilo
`<algoritmo de calibración, entorno> -> resultados de calibración`
pero cómo estructuro esa data?
Es necesario alcanzar un punto de corte en el cual el experimento queda fijo y
empiezo a tomar datos?
O puedo ir modificando el experimento más adelante?
Si modifico el experimento pierdo la data anterior, queda incompleta?

#### Observaciones preliminares de webgazer

La calidad de las predicciones parece verse principalmente afectada por el
movimiento relativo entre los ojos y el lente.
Esto incluye al menos distancia a la cámara, ángulo de la mirada, rotación de la
cabeza.
Distintos niveles de luz o la posición de la notebook parecen afectar menos.
La variación de luz entre calibración y experimento sí parecieron afectar la
calidad de los resultados.

El empeoramiento de las predicciones debido al movimiento de la cabeza se
arrancá a ver casi de inmediato:
mantener la cabeza fija durante la calibración para luego relajarla durante el
experimento de validación duplicaba el error promedio en píxeles de predicción
frente al caso en el cual se mantenía siempre fija la cabeza o siempre relajada.

Mover o rotar la cabeza durante la calibración mejoraban las predicciones luego,
lo cual da lugar a preguntarse cómo conviene hacer la calibración.
Herramientas online como
[https://app.gazerecorder.com/](https://app.gazerecorder.com/)
explícitamente piden mover la cabeza durante la calibración.

También entra en duda si para distintas categorías de experimentos tendría
sentido realizar distintas calibraciones.

### Implementación

Voy a apuntar a crear alguna capa lógica entre el eyetracker que use y el resto
del código.
De momento nomás voy a andar probando con webgazer pero como librería no me da
mucha confianza y como eye tracker no parece tener un buen algoritmo de
calibración.

### Librerías que hay dando vueltas

[WebGazer](https://webgazer.cs.brown.edu/) parece ser la única librería abierta
que efectivamente provee eyetracking en el browser.
Está tmb [SeeSo](https://seeso.io/) pero es paga y cerrada (proveen un SDK).
Después hay otro set que son herramientas proveen eyetracking como un servicio
más que como librería ([GazeRecorder](https://app.gazerecorder.com/), 
[RealEye](https://www.realeye.io/); tmb pagas).
Hay algunas librerías que proveen tracking (face tracking, feature detection)
pero no eye tracking ([headtrackr](https://github.com/auduno/headtrackr),
[tracking.js](https://github.com/eduardolundgren/tracking.js/)) ni están
mantenidas.
