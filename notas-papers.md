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
