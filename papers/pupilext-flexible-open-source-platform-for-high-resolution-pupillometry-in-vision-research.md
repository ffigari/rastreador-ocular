## pupil-ext

PupilEXT: Flexible Open-Source Platform for High-Resolution Pupillometry in Vision Research

(Introduction)

Software open source de detección de pupila.
El software industrial no es abierto, en particular el algoritmo utilizado no
puede diagnosticarse cuando genera una predicción errónea.
Es aplicación nativa, no sé si se pueda enganchar con el browser.
Requiere cámaras industriales, en particular cámaras basadas en "near-infrared (NIR) illumination".

Provee 6 algoritmos para detección de pupila (Starburst, Swirski, ExCuSe, Else, PuRe and PuReST)

(The Rising Popularity of Pupil Light Response Research)

El estudio de cómo la pupila reacciona a la luz es actualmente popula y requiere
mediciones precisas ("amplitudes in the range of 0.1 to 0.4 mm are captured
accurately to specify intrasubject variability").
La popularidad demanda también herramientas generales que permitan lograr
resultados comparables entre distintos estudios ("requires additional efforts in
terms of standardization and provision of consistent tools, contributing to
comparability in measurement and pre-processing methodologies")

(The Issue of Pupillometry)

Los eye trackers con equipamiento especializado salen entre 5000 y 40000 euros
pero las cámaras industriales en sí rondan 200 a 600 euros. El costo adicional
proviene del software agregado y de las licencias. ("Thus, the price gap from
commercial products results from the integrated software and license fees")

Los sistemas comerciales son cerrados. Se dificulta reproducibilidad, no puede
realizarse validación propia.
Pupil Labs es abierto open source pero el diametro absoluto de la pupila se
calcula con un método cuya preición de conversión no está validado (va mejor
para experimentos donde alcance usar diametro relativo).
EyeRecTooA es abierto, está diseñado para head mounted eye trackers y webcams lo
cual puede andar para nuestro caso de uso ("the software is mainly designed for
head-mounted eye trackers or webcams and the use-cases are not targeted for the
experimental pipeline of pupil research under laboratory conditions")

pupil-ext busca imitar esto de pupil labs de orientarlo a end-users

(Choosing Pupil Detection Algorithms for PupilEXT)

La detección de la pupila usa fuertemente el contraste entre la esclerótica y el
iris de la pupila, aunque state of the art algorithms tienen pasos extra en el
pipeline.
Edeges detection es muy importante para poder garantizar el rendimiento del
algoritmo

Una razón por la cual se usan cámaras infrarojas es que son menos afectadas por
reflejos de la luz en la pupila ("Under laboratory conditions, eye images are
mainly captured using a NIR light source to avoid cornea reflections of the
ambient environment")

El setup de iluminación influencia qué algoritmo se utiliza para capturar las
imágenes. Se distinguen por la posición relativa entre el emisor de luz
infraroja y la cámara que captura tales frecuencias (off axis o alineado).
Según qué se use se obtiene contraste negativo o contraste positivo. Hay
algoritmos que combinan ambos métodos pero que requieren capturar dos frames
por cada sample ("two frames are needed for each captured pupil size value,
reducing the overall sampling rate")

Sin embargo el core de pupil peasurment systems está en estimar el tamaño de la
pupila. De los 35 algoritmos que eligieron analizar se quedaron con los que
estuvieran basados en dark pupil detection (off axis source lights) y que
tuvieran alguna implementación en c++. Tmb dejaron de lado aquelos que
estuvieran basados en redes neuronales.

Se elige uno de los algoritmos por defecto pero el usuario puede elegir.

(Hardware Set-Up of the Camera System)

Eligen una marca de cámaras especial. Conscientemente no soportan consumer
webcams porque "PupilEXT is intended for reliable and accurate research
applications".

basado en dos cámaras. sinronizadas con trigger via hardware ya que el trigger
por software no es preciso ("a software trigger that cannot guarantee
synchronized image acquisitions")

cuando se tiene una cámara el diámetro de la pupila se obtiene en píxeles. dsp
con capturando algún objeto de referencia se puede estimar el diámettro en
píxeles.

permiten grabar el video sin detección de pupilas, para luego realizar el
procesamiento de manera online. tmb proveen software e instrucciones para
adaptar el setup propio tal que la cámara pueda filtrar la luz que no es
infrarroja

(Camera Set-Up)

(Embedded Hardware Trigger)

(The Cross-Platform Software Suite)

Definen interfaces para poder usar los distintos algoritmos de detección de la
pupila

(Camera Interface)

el trigger de la cámara via software es necesario nomás para el setup stereo
por esto de tener que sincronizar el frame capturado por ambas cámras. en el
setup de una cámara no es necesario.

Se proveen tres interfaces para los objetos de las cámaras: single camera, file
camera (para el caso offline), stereo camera (cámara principal + cámaras
secundarias)

(Image Recording and Reading for Offline Analysis)

qué formato se elige para guardar las imágenes. BMP mantiene la calidad pero
puede ser demasiadado pesado. JPEG puede ser más accesible en términos de disco
pero comprime la data.  Con HDD comentan sólo poder usar JPEG para los dos
tipos de setup. Con un SDD en teoría podrían usar BMP

(Pupil Diameter Recording)

cada medida de la pupila (en los casos no offline) está asociado al timestamp
de UNIX. El diámetro de la pupila se reporta en píxeles y en el caso stereo tmb
en milímetros

algunos de los algoritmos ofrecidos proveen valores de confidence. además la
plataforma provee un valor de confidence basado en el contraste de la
predicción ("based on the outline contrast of the inner and outer regions of
the fitted ellipse")

(Camera Calibration)

[Zhang, Z. (2000). A flexible new technique for camera calibration. IEEE Trans. Pattern Anal. Mach. Intell. 22, 1330–1334. doi: 10.1109/34.888718]
"We propose a flexible technique to easily calibrate a camera. It only requires
the camera to observe a planar pattern shown at a few (at least two) different
orientations."

[https://la.mathworks.com/help/vision/ug/camera-calibration.html]
"Geometric camera calibration, also referred to as camera resectioning,
estimates the parameters of a lens and image sensor of an image or video
camera. You can use these parameters to correct for lens distortion, measure
the size of an object in world units, or determine the location of the camera
in the scene."

(Implementing Single-Camera Calibration)

utilizan feature detection en 30 imagenes para determinar los parámetros de
calibración. "This function optimizes the camera parameters by minimizing the
reprojection error" (zhang 2000)

(Stereo Camera Calibration)

(Demonstration of a Measurement Pipeline With PupilExt)

el uso que muestran para el setup incluye las condiciones de labortorio
respecto del control sobre la cabeza (chin rest, "a subject looked into a 700
mm × 700 mm sized homogeneously illuminated observation chamber")

(Pre-processing the Measured Raw Data)

recomiendan descartar las medidas cuyo "confidence measure" esté por debajo de
1 y aquellas cuyo "axis ratio" haya variado mucho (debería mantenerse más o
menos constante)

(Comparison of the Pupil Detection Approaches)

los algoritmos distintos algoritmos disponibles se evalúan según su capacidad
de estimar el centro de la pupila

explican un poco cómo anduvo cada algoritmo y comparan la cantidad de
parámetros requeridos

(Validation of the Pupil Detection Algorithms)

el diámetro de la pupila debería ser más o menos constante durante todo el
experimento.  eliminar los valores con poca confianza ayuda a lograr esto, en
particular evitando imprecisiones causadas por los pestañeos

"The proposed technique for detecting eye blinks based on an outline confidence
is highly affected by the detection rate. For example, it is no longer possible
to distinguish between a false pupil fit or a closed eyelid at a higher rate of
pupil detection artifactsx"

menor cantidad de parámeteros libres son preferibles porque hay menos chance de
pifiarle y obtener malos resultados

los algoritmos que fallan menos del 10% y que tienen pocos parámetros son
comparados luego según su capacidad de reportar un valor estable para el
diámetro de pupila. la media de las diferencias puede diferir 0.001 mm según qué
algoritmo se elija.

(Determining the Pupil Measurement Accuracy)

en la validacion stereo se reporta el MAE de las reproyecciones que se calculan
al calibrar la cámara pero esto no incluye las inexactitudes del algoritmo de
deteción de pupila. para medir esto un poco miden un objeto circular de 5mm
puesto frente al ojo del sujeto. obtienen un MAE de 0.014mm inicialmente y de
0.0059 cuando aplican los filtros mencionados arriba. hubo picos de 0.1mm. hay
que notar tmb que esa validación se hace con un objeto estático

(Limitations of the Proposed Pupillometry Toolbox)

el algoritmo este funciona par aun único ojo. usando ROI en la GUI se puede
limitar qué va a mirar el algoritmo.

lo que dan armado está listo sólo para una marca de cámaras, aunque la interfaz
provista permitiría agregar otras cámaras. Además se puede grabar offline con
cualquier cámara y dsp proveer las imágenes al software

usan sólo CPU cuando se podría usar GPU. el frame rate está limitado por el poder
de cómputo de la máquina que estén usando.

(Discussion)

hay otros trabajos empujando para lograr herramientas open source. La confianza
de las métricas sobre la pupila no suelen ser reportadas porque no son
exportadas por las herramienta, al margén de que existen métricas que pueden
reportarse

la bibliografía actual no suele dar atención a los posibles errores técnicos o de
software. en sistemas cerrados se hace imposible hacer validaciones. este trabajo muestra
además que para la misma data y distintos algoritmos pueden ocurrir errores de hasta
0.05mm.

Las especificiaciones del setup o el reporte del centro de la pupila no serían
suficiente para lograr que los resultados de distintos trabajos sean
comparables, o para garantizar la reproducibilidad de los experimentos.
Idealmente se podría unificar el mecanismo con el cual se captura la
información de la pupila, reduciendo así la brecha entre distintos algoritmos.
"From our perspective, a uniform measurement platform is essential for
pupillometry, ensuring comparability and reproducibility." Reportar el error
sobre un objeto de referencia permitiría comparar los distintos trabajos.
