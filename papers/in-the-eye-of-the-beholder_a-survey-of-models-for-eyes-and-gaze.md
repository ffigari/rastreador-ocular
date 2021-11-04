# in-the-eye-of-the-beholder_a-survey-of-models-for-eyes-and-gaze

In the Eye of the Beholder: A Survey of Models for Eyes and Gaze

## Introduction

Robust non-intrusive eye detection and tracking is, therefore, crucial for the
development of human-computer interaction. Se distinguen eye detection y gaze
detection, eye detection dividido en la deteccion de la existencia de ojos, en
interpretar precisamente la posición de los ojos y en el caso de los videos el
seguimiento de la posición de los ojos.

## Eye models for eye detection

La apariencia de los ojos comparte características entre todos los individuos
pero pequeñas variaciones (eg el ángulo de la mirada) impactan fuertemente en la
apariencia. Existe por lo tanto mucho research que constantemente busca salvar
estos problemas. Otras aplicaciones de visión por computadora tienen problemas
similares pero en órdenes de magnitud menores y con menor frecuencia. Algunos
ejemplos de estas dificultades son ethincity, viewing angle, posición de la
cabeza, luminosidad, la posición del iris, si el ojo está cerrado o abierto.

Las técnicas de detección de ojos se distinguen en shape based (basado en
obtener features de los ojos; dividido en fixed shape y deformable shape),
appearance based (basado en usar un patch del ojo; dividido en intensity y
subspace based) e híbridos.

### Shape based approach

An important property of these methods is their general ability to handle
shape, scale, and rotation changes.

simple elliptical. Alcanza con trackear el iris o la pupila, que pueden ser
trackeados con cinco parámetro.

complex shape. Se utilizan dos parábolas y un círculo para modelar el ojo. Es un
template deformable y permite mayor detalle en el modelo.

### Feature based shape approach

Busca identificar features (limbus, pupila, reflección de la cornea) para
localizar la posición del ojo.

local features by intensity. Aprovechar los contornos detectables by gray-level
differences.

local features by filter esponses. Utilizar un banco de filtros para enfatizar
características deseables e idealmente desenfatizar las no deseables.

si se tiene suficiente detalle, se puede buscar capturar específicamente la
pupila, aunque suele ser más apropiado para cuando se cuenta con iluminación IR.

estos métodos están limitados por no poder reconocer cuando el ojo se cierra, lo
cual no está resuelto. Serían sin embargo resistentes a cambios de iluminación

## Appearance based methods

Basado en la apariencia fotométrica, aplicable a imágenes en general. Suelen
llevarse a cabo en un dominio espacial o transformado. No aplican muy bien para
detectar rotaciones o scaling. Suelen además requerir capturar grandes
cantidades de datos previos.

Una solución efectiva y simple es usar template-based correlation. Para
localizar el ojo precisamente se suele necesitar procesamiento extra. Subspace
methods pueden mejorar la eficiencia gracias a reducción de la dimensionalidad.
Una opción es buscar un círculo homogeneamente negro luego de detectar la
posición general del ojo.

## Hybrid models

existen varias propuestas que combinan shape y appearance based methods. Por más
que la distribución de colores sea diferente que su entorno, existe poco trabajo
que busque construir modelos basados en colores.

## Otros métodos

### Iluminación IR

El uso de luz infrarroja es transversal al resto de los métodos. Los que
utilizan esta luz se llaman active light approaches. La luz IR no distrae al
sujeto. Existe bastante investigación sobre la relación entre la intensidad del
brillo de la pupila y parámetros como la posición de la cabeza, la dirección de
la mirada y el background étnico.

bright/dark pupil effect. El efecto de la emisión de luz es distinto si el
emisor comparte el eje con la cámara (on-axis) que si no lo hace (off-axis).

Objetos en el fondo puede confundirse con la púpila. Mezclar luces onaxis y
off-axis permite mitigar esto pues el efecto mencionado aplica únicamente sobre
la pupila. Este mecanismo requiere sin embargo sincronizar emisores de luz con 
las cámaras.

### Blinks and motion

Trabajos recientes utilizan los pestañeos para detectar la posición de los ojos
utilizando frames sucesivos, heuristicias y suponiendo una una posición fija de
la cabeza. Pestañeos rápidos y movimientos de la cabeza dificultan lograr buenos
resultados.

### Discussion

Los métodos se distinguen por sus propieades geométricas y fotométricas. A
distintos entornos existen distintos métodos que dan mejores resultados.

Existen datasets para validar eye detection. Los requerimientos sobre las
imágenes de los ojos varían según método. Los métodos presentados pueden
extenderse a la detección de otros objetos.

## Gaze estimation

gaze should be undestood as eiter the "gaze direction" or the "point of regard".
fixation, saccades, smooth pursuits. Properties of saccades and fixations may
provide diagnostic data for the identification of neurological, vision or sleep
disorders.

several reflections occur on the boundaries (light source -> cornea -> sclera
-> lens). glint = la refleccion sobre la cornea de la luz

a persons gaze is determined by the head pose and eyeball orientation. la
cabeza suele moverse a una posicion comoda respescto de lo que se quiera mirar.
La posición de la cabeza suele dar una buena idea a grandes rasgos de donde está
mirando el sujeto. Implicita o explícitamente necesita entonces modelarse tanto
la cabeza como las pupilas.

Se distinguen los siguientes procedimientos para una calibración:
camera-calibration, geometric-calibration (determinar la ubicación y
orientaciones de los distintos elementos del setup como light sources y
camaras), personal-calibration (cornea curvature), gazing mapping calibration.

Idealmente un gaze tracker debería minimizar obstrucción e intrusividad. Con el
paso del tiempo los trackers se acercan más a ese ideal.

### Feature based gaze estimation

estimación usando features locales (contours, eye corners reflections). Se
subdividide en interpolation based (se asume un mapeo entre features y gaze
coordinates) y model based (se computa the gaze direction directo).

#### 2D regression based gaze estimation

Muchos single glint methods asumen erronameante que que la superficie de la
cornea es un espejo perfecto y que el glint permance estatico cuando gira la
cornea. Se usa la diferencia entre el centro de la pupila y el glint para
estimar la mirada.

Con el tiempo aparecieron sistemas que tienen en cuenta esa no-linearidad. Otros
sistemas usan dos fuentes de luz lo cual daría mejores resultados. Hay propuestas
de usar redes neuronales para estimar la mirada.

Two-dimensional interpolation methods do not handle head pose changes well.
Garantizar head movement invariance no es un problema bien resuelto.

#### 3D model based gaze estimation

se modela la geometría 3d de los ojos y dsp se interseca gaze direction vector
con el monitor.

Euclidean relations such as angles and lengths can be employed through
calibrated cameras. The general approach is to estimate the center of the
cornea, and thus, the optical axis in 3D. Points on the visual axis are not
directly measurable from the image. By showing at least a single point on the
screen, the offset to the visual can be estimated. The intersection of the
screen (known in fully calibrated setups) and the visual axis yield the point
of regard.

Los distitnos métodos puede categorizarase según cuántas cámaras y cuántas luces
usan.

### Other methods

#### Appeareance based methods

En lugar de extraer features se usa el contenido de la imagen para mapear
directo a la pantalla. Se espera que la funcion de mapeo se extraiga
implicitamente. No suelen requerir calibración de cámara y geométrica pero
suelen requerir mayor cantidad de puntos de calibración. No se reportaron
métodos con head pose invariance.

#### Natural light methods

Natural light approaches face several new challenges such as light changes in
the visible spectrum, lower contrast image. Methods using visible may also
employ corneal reflec- tions since the results obtained using IR are also
applicable to visible light. The difference is that the required image features
are less accurately depicted in the images, and that visible light may disturb
the user and cause the pupil to contract.

#### Dual Purkinje

Basado en aprovechar que una misma fuente de luz puede generar múltiples
reflecciones debido a la estructura del ojo, produciendo así varios glints.
Puede conseguirse mayor precisión pero se requieren condiciones de luz bien
controladas debido a que algunas de las reflecciones utilizadas son débiles.

### Discussion

Gaze estimation implica múltiples variables y puede ser acercado con varias
técnicas. Los acercamientos más sencillos son interpolation based dos
dimensionales con una cámara pero no suelen manejar movimientos de cabeza. Un
modelo que sea invariante a los movimientos de cabeza suele implicar el uso de
dos emitores de luces. Modelos que buscan capturar la geometría 3D pueden
incluso ser robustos respecto de los movimientos de cabeza.

Comparar los resultados de los distintos eytrackers expuestos en la bibligrafía
no es preciso ya que no hay un estnadar respecto de como reportar los datos.

Las estimaciones en los bordes de la pantalla son menos precisas. El uso de
anteojos empeora los resultados de la estimaciones.

La calidad y cantidad de hardware tiene un impacto directo sobre los resultados
obtenidos. Sin embargo, el nivel de precisión requerido varía según la
aplicación por lo que el uso de eyetrackers basados en cámaras web puede ser 
suficiente. La combinación de técnicas de distintas categorías tiene el
potencial de capturar sus distintos beneficios.

## Eye detection and gaze tracking applications

En muchas aplicaciones de visión por computadora la detección de los ojos y de
la mirada suele ser de los pasos más importantes. Esta detección es una
herramienta poderosa para el estudio of real time cognitive processing and
information transger. Se distinguen principalmente dos campos, el del
diagnóstico (eg, para permitir el análisis y la compresión de la atención
humana) y el de la interactividad (eg, eye typing).

## Summary and conclusions

Por más que se realizó mucha investigación sigo habiendo mucho espacio para
mejora. El cambio de la pose de la cara y de la luz sigue siendo un problema.
Existe un tradeoff entre calidad del setup y su algoritmo vs la robustez de los
resultados. Los sistemas de eyetracking tienen el potencial de ser económicos,
fáciles de instalar y requiriendo mínima calibración. Algunas posibles rutas a
explorar son limitar el uso de luz IR, head mounts, flexibilizar el setup,
limitar la necesidad de una calibración explícita, reducir los costos o mayor
tolerancia a variaciones como el uso de anteojos.

El desarollo de sistemas más económicos podría lograr mayor accesibilidad de la
estimación de la mirada como herramienta para el público general pero podría en
paralelo lograr resultados menos precisos. En particular debe lidiarse con
mayores niveles de ruido. Queda entonces también espacio para mejorar la
interpretación de la mirada.

La complejidad y variabilidad de la apariencia de los ojos hacen de la
estimación de la mirada un problema naturalmente complejo. Asimismo, mejorar los
sistemas de estimación de mirada implica mejoras en otros campos (eg, el rastreo
de ojos en video) por lo que es de creciente interés la investigación en este
área.
