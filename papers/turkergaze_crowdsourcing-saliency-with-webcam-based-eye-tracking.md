# TurkerGaze

TurkerGaze: Crowdsourcing Saliency with Webcam based Eye Tracking

## Introduction

Es difícil construir datasets que requieran eyetracking por todo esto del
equipamiento costoso. Para su caso (saliency) parece que no se necesita una
precisión absoluta. "We designed our system around the following criteria:
ubiquitous hardware, ease of set-up, sufficient quality for saliency data
collection, and real-time performance."

## Related works

Existen dos categorías de algoritmos para gaze estimation:
- feature based: se basan en extraer detalles de los ojos como el iris;
  requieren cámaras infrarrojas de mucha calidad; depende fuertemente de la
calibación
- appearance based: usan la imagen de los ojos como un high-dimensional vector;
  se construye un modelo de aprendizaje automático; varios de los algoritmos
propuestos asumen que la cabeza no se mueve; los movimientos de cabeza
fácilmente causan drift y las propuestas para combatirlo suelen implicar volver
a mostrar puntos para calibrar

Otras propuestas son:
  - que el usuario reporte donde estuvo mirando, pero solo se puede reportar un
    punto por imagen
  - usar mouse tracking saliency maps, pero el movimiento del mouse es más
    lento que el de los ojos así que no es evidente que pueda aplicarse a video

En el pasado ya se usó eyetracking para construir datasets de fixations en
imágenes y videos.  Difieren en múltiples parámetros (cantidad y estilo de los
videos). En particular algo que podrían lograr con este trabajo es construir
datasets de saliency con muchos participantes.

## Large-scale crowd-sourcing eye tracking

### Design considerations

- Entorno del experimento: A diferencia del laboratorio no se tiene control
  sobre múltiples variables como la luz o la posición de la cabeza
- Hardware: sólo se necesita webcam y un browser pero aun así hay participantes
  que deben ser dejados de lado por no cumplir
- Software and real time performance: hay que ser astutos con el uso de
  recursos para garantzar real time estimations. Esto permite dar feedbcak
online (lo cual atrae la atención) y evitar grabar video
- Head movement: si el algoritmo se diseña para mantener la cabeza fija entonces
  hay muchas chances de que ande mal con leves movimientos
- Lack of attention: hay que dar instrucciones claras al usuario para asegurar
  la atención del participante

### Webcam based gaze prediction algorithm

Obtienen facial landmarks usando clmtrackr. Hay un pococ de jittering así que
los estabilizan con un suavizado temporal a través de un filtro Kalman. Tmb
definen un tamaño mínimo para el tamaño de la imagen del ojo.

Calibran mostrando una serie de puntos durante un segundo cada uno. Se usan los
últimos frames para calibrar. Luego computan Zero Mean Normalized
Cross-Correlation para detectar y filtrar los pestañeos.

Para la estimación reducen el tamaño de la imagen de los ojos a 6x10pxs "and
then performed histogram normalization". Muchas dimensiones con pocos datos es
propenso a overfitting. Luego usan Ridge Regression "to achieve real-time
performance for online applications"

### Game design for crowdsourcing

Las dificultades presentadas por el entorno hacen crucial pensar la UX y la UI.

La principal causa de falla son los movimientos de la cabeza. En lugar de
explícitmaente permitir movimientos de cabeza, piden a los participantes que
tengan la cabeza lo más fija posible usando algún soporte improvisado.
Adicionalmente checkean [cómo?] y recalibran frecuentemente y realizan tareas
cortas.

Sandwichean calibraciones y validaciones. Para el experimento final reentrenan
un modelo en base a los datos recolectados. Para eliminar outliers utilizan
cross validation y en particular leave-one-out error.

Una alternativa a la recalibración es darle a los experimentos una duración
menor a un minuto. También buscan detectar movimientos de cabeza para solicitar
al participante que reposicione la cabeza. Si se detecta un movimiento muy
grande también puede reiniciarse el experimento. Miden además la intensidad de
la luz para saber si tienen que pedirle que ajuste la luz. Finalmente piden
como mínimo una resoluicón de 1080x720 para la cámara y un frame rate de 25fps
mientras se corre el facial landmark tracking.

Los sujetos pueden distraerse o no seguir las intrucciones. Usan imagenes de
saliency existentes para intentar detectar cuando ocurre que un sujeto se
distrae. También dan feedback al usuario con el fin de mantenerlo motivado.

Armaron dos interfaces basadas en juegos (angry birds, whac-a-mole) para obtener
una experiencia más atrayante y familiar. Dentro de estas interfaces integran
calibración y quality control.

### Experimental setup

No pueden usar métodos estandar para detectar fixations por el low sample rate
que usan así que lo resuelven con clustering ("so instead we used meanshift
clustering in the spatio-temporal domain")

## Evaluation

### Gaze prediction accuracy

Para validar las estimaciones de la mirada comparan con un eyetracker comercial
tanto para puntos uniformemente aleatorios como para mirada libre en la
pantalla. Para realizar la evaluación de calidad usan sólo los últimos 0.5
segundos de los 1.5 que muestran cada estímulo.

También comparan la calidad del scan path obtenido por ambos eyetrackers.

### Fixation estimation and saliency maps

Usando trabajos previos (Judd et al, 2009) arman un dataset de ground trouth
para el saliency de algunas imágenes

"the AMTurk saliency map is similar to top performing models by various AUC
metrics."
