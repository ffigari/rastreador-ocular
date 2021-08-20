# rastreador-ocular

## Implementación

Con `./install.sh` se instalan las dependencias.  
El entry point es `index.html`.
Se puede hacer `firefox index.html` por ejemplo.

## Notas

Estimación de mirada en experimentos en navegador y sin interacción continua
por parte del usuario.

### Trabajo relacionado

Los sistemas existentes que involucran eye tracking son cerrados y requieren
equipamiento especializado a utilizar en laboratorio. Esto presenta múltiples
trabas a la utilización de eye tracking como herramienta. Inicialmente, el costo
de los sistemas existenes puede ser prohibitivo [2]. La necesidad de
equipamiento especializado obliga a los sujetos a estar presentes en donde este
esté localizado [3]. La reproducibilidad es también un problema, pues no existen
implementaciones ni formatos de reportes de error estándar [1]. Varias de las
opciones que ofrece el mercado son además cerradas por lo que no se pueden
validar ni los algoritmos utilizados ni los datos reportados.

En los últimos años surgieron herramientas como PupilEXT (PE), WebGazer (WG) o
TurkerGaze (TG) cuyo mayor punto en común es la eliminación de equipamiento
especilizado. PE provee software de detección de pupilas así como instrucciones
sobre como instalarlo en cámaras propias. Esto reduce el costo de construir un
setup pues el costo de estos sistemas está relacionado al valor agregado por el
software [3]. TG y WG corren directamente sobre navegadores web y utilizan
cámaras domésticas. TG por su parte está centrada en la construcción de saliency
datasets, mientras que WG busca proveer estimación de miradas para uso general.

WG parece ser la única opción existente para un sistema de eyetracking abierto
y basado en webcams domésticas. Su mecanismo de calibración se basa sin embargo
en la recalibración constante a través de las interacciones del usuario con el
navegador. Es por lo tanto ineficaz para experimentos en los cuales durante los
mismos no haya interacciones por parte de los sujetos.
[SeeSo](https://seeso.io/) provee eyetracking pero de manera paga, cerrada y a
través de un SDK. Otras herramientas como
[GazeRecorder](https://app.gazerecorder.com/) o
[RealEye](https://www.realeye.io/) proveen eyetracking como servicio lo cual
evita que se les de un uso general. Librerías como
[headtrackr](https://github.com/auduno/headtrackr) o
[tracking.js](https://github.com/eduardolundgren/tracking.js/) ofrecen face
detection o feature detection pero ninguna ofrece detección de pupilas o
estimaciones de miradas. Tampoco pintan tener mucho mantenimiento.

#### Algoritmo de WebGazer

WG calibra el sistema con cada click y con movimientos del mouse cada a lo sumo
50ms. Simplifican el problema asumiendo que la mirada y estos eventos se
alinean perfectamente por más que otros trabajos hayan mostrado que no es
cierto. Hay correspondencia entre mirada y eventos [cita?] pero existe también
un delay que depende de cada evento [4]. Los datos se agregan al modelo a
medida que ocurren. Los pares [imagen de los ojos, coordenada] se utilizan para
entrenar el modelo.

En cada frame se realiza una predicción nueva. Para ello recuperan la imagen de
los ojos y predicen luego la coordenada mirada en la pantalla. Opcionalmente
para la predicción se puede aplicar un filtro Kalman.

No se realiza ningún ajuste ante movimiento de la cabeza, pues se asume que el
sistema se va a ir recalibrando a lo largo del tiempo con los eventos de los
usuarios.

### Dificultades propias de estimación de mirada via webcam

#### Entorno no controlado

Tradicionalmente los experimentos de eye tracking se realizan de manera
controlada dentro de un laboratorio. Esto permite ajustar luminosidad y
posiciones de las cámaras según convenga al setup que se utilice. Un supervisor
puede además asistir al sujeto a acomodarse correctamente.

En un contexto remoto se pierde el control sobre estas variables. La luminosidad
inicial puede no ser ideal pues el sujeto puede estar a contra luz o en la
oscuridad. Podría además modificarse durante el experimento. Tampoco se tiene
control sobre los movimientos de la cabeza o del cuerpo que el sujeto pudiera
realizar. El posicionamiento del dispositivo utilizado impacta también en la
calidad de los resultados. En un laboratorio puede preverse donde se sentará el
sujeto y cómo se posicionarán las cámaras.

#### Calidad de las imágenes

Los eyetrackers profesionales y PE utilizan cámaras infrarrojas de alta
precisión. La luz natural causa reflejos en los ojos que dificultan estimar la
posición de los ojos y en consecuencia las estimaciones relacionadas [1]. La
calidad de las imágenes obtenidas puede además no ser suficiente para aplicar
algoritmos tradicionales de eyetracking [3].

#### Variabilidad del hardware

Distintos sujetos tendrán distintos dispositivos. En particular variarán las
resoluciones de las cámaras web y el poder de cómputo. Al momento de iniciar
experimentos deben verificarse las características del setup del sujeto.
Previamente deben establecerse criterios mínimos para permitir el inicio del
experimento.

### Algoritmo de estimación de mirada

#### Captura de datos

Los algoritmos pueden agruparse en feature based y appeareance based. Los de la
primera categoría suelen requerir cámaras especializadas (infrrojas y de buena
definición) por lo cual no serían apropiadas para nuestro caso de uso [3].

El dato central que debe capturarse es la posición de la pupila. Inicialmente
debe detectarse la cara del sujeto. Dentro de estas capturas deben capturarse un
bounding box de los ojos. Esto debe hacerse en tiempo real para cada frame al
mismo tiempo que se realizan calibraciones y estimaciones. Debe entonces
encontrarse algún balance entre la frecuencia de sampleo y la capacidad del
hardware del sujeto.

#### Calibración

Los sistemas de eyetracking requieren ser calibrados para lograr acomodarse a la
mirada de cada sujeto. La alternativa común es recolectar datos inicialmente
para luego construir el modelo que estima la mirada. Esta recolección suele ser
explícita y mostrando una serie de estímulos que el sujeto debe seguir. Como
alternativa puede mostrarse un videojuego que obligue al usuario a interactuar
utilizando la mirada [3]. Otras soluciones evitan la calibración inicial
explícita para en lugar calibrar a medida que ocurren interacciones por parte
del sujeto [2, 4].

Lograr generalizar en base a la calibración parece ser difícil. Experimentos
preliminares con JSPsych + WG mostraron que una leve relajación de la cabeza
podía duplicar el error promedio de las estimaciones. Se vió también que hacer
movimientos explícitos durante la calibractión mejoraban los resultados. La
herramienta GazeRecorder mencionada previamente pide explícitamente al usuario
realizar movimientos con la cabeza durante la fase de calibración.

La duración de la calibración debe tenerse en cuenta al momento de diseñarla
pues el tedio generalmente asociado a esta fase podría afectar la atención del
sujeto [3]. Debe entonces encontrarse un balance entre la cantidad de estímulos
mostrados y la duración durante la cual se muestra cada uno de ellos.

Es también posible que la calibración pueda optimizarse según el experimento
que se vaya a correr. Se distinguen por ejemplo si se busca detectar
fixaciones, sacadas o seguimientos o si únicamente debe detectarse a qué lado
de la pantalla está mirando el sujeto. Esta información extra permitiría
diseñar una calibración orientada a capturar luego específicamente los
movimientos deseados.

Otro interrogante es qué datos de la calibración usar para entrenar nuestro
modelo. Los estímulos que se muestren al sujeto se considerarán como los datos
ground truth de la dónde está mirando. Sin embargo el sujeto no estará mirando
realmente al estímulo durante el intervalo en el cual cambia la vista para
mirarlo. No es evidente entonces cuáles de estos pares deben usarse para
entrenar el modelo. TG utiliza los últimos 0.5 segundos de los 1.5 segundos que
muestra el estímulo, mientras que JSPsych + WG utiliza únicamente el par al
momento del click.

[ Cómo afecta el acostumbramiento a la calibración a los resultados ]

#### Validación

Posterior a la calibración, es común [citas?] realizar un experimento de
validación para determinar la calidad resultantes de las estimaciones. En base
a sus resultados puede decidirse si continuar o no con el experimento siguiente.
Puede además darnos algún criterio de comparación entre resultados de distintos
sujetos.

Una alternativa común para realizar la validación es mostrar los mismos
estímulos mostrados durante la fase de calibración. Surgen entonces los mismos
interrogantes sobre qué datos recolectar.

#### Drifting y recalibración

Los sistemas en cuestión se descalibran con el paso del tiempo. En particular
esto ocurre frente a movimientos de la cabeza. Sistemas tradicionales suelen
asistir al sujeto con alguna estructura para apoyar la cabeza [cita?] pero esto
no es posible en nuestro contexto remoto. Ante las dificultades de permitir
movimiento libre de la cabeza surge la necesidad de indicar al usuario de
posicionarse en alguna posición que facilite quedarse quieto [3].

[ Hay que medir el drifting ]

Nuestro contexto no garantiza interacciones (eg, clicks) por parte del sujeto
por lo que intentar mapear interacciones con la mirada no sería una solución.
Otra alternativa común es realizar recalibraciones a medida que ocurren los
experimentos. Se pueden incluso realizar múltiples rondas de calibración y
validación previo al experimento [3].

Una forma de reducir el efecto del drifting es realizar experimentos cortos
seguidos de recalibraciones. No es evidente qué tan cortos deban ser los
experimentos.

### Referencias

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

- [
  [3] TurkerGaze: Crowdsourcing Saliency with Webcam based Eye Tracking
](
  /papers/turkergaze_crowdsourcing-saliency-with-webcam-based-eye-tracking.md
)

- [4] PACE: Building a Personalized, Auto-Calibrating Eye Tracker from User Interactions

#### otros que podría ser interestante leer, en ningún orden particular:

- T. Judd, K. Ehinger, F. Durand, and A. Torralba. Learning to predict where humans look. ICCV, 2009
- Y. Sugano, Y. Matsushita, Y. Sato, and H. Koike. An incre- mental learning method for unconstrained gaze estimation. ECCV, 2008
- Dan Witzner Hansen and Qiang Ji. In the eye of the beholder: A survey of models for eyes and gaze. IEEE TPAMI, 32(3):478—500, 2010.
- Zhang, Z. (2000). A flexible new technique for camera calibration. IEEE Trans. Pattern Anal. Mach. Intell. 22, 1330–1334. doi: 10.1109/34.888718
- Holmqvist, K., Nyström, M., and Mulvey, F. (2012). “Eye tracker data quality: what it is and how to measure it,” in Proceedings of the Symposium on Eye Tracking Research and Applications ETRA ‘12, (New York, NY: ACM Press), 45. doi: 10.1145/2168556.2168563
- Arvin, S., Rasmussen, R., and Yonehara, K. (2020). EyeLoop: an open-source, high-speed eye-tracker designed for dynamic experiments. bioRxiv [Preprint]. doi: 10.1101/2020.07.03.186387
- Santini, T., Fuhl, W., Geisler, D., and Kasneci, E. (2017). “EyeRecToo: open-source software for real-time pervasive head-mounted eye tracking,” in VISIGRAPP 2017 Proceedings of the 12th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications, (Setúbal: SciTePress), 96–101. doi: 10.5220/0006224700960101
- Santini, T., Fuhl, W., and Kasneci, E. (2018a). PuRe: robust pupil detection for real-time pervasive eye tracking. Comput. Vis. Image Underst. 170, 40–50. doi: 10.1016/j.cviu.2018.02.002
