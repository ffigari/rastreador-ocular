# rastreador-ocular

## Desarollo

### módulos de js + plugins

`./install.sh` para instalar las dependencias.  
`node index.js` para buildear el js.
La versión de `node` requerida está dentro del archivo `.nvmrc` por lo que puede
usarse `nvm use` (luego de instalar al menos una vez con `nvm install`) para
cambiar a la versión requerida (https://github.com/nvm-sh/nvm).

Dps el entry point es `index.html`, con abrirlo en un navegador se pueden usar
los experimentos armados. Se puede por ejemplo hacer `firefox index.html`.

### data analysis

Setear el entorno:
```bash
python -m venv rastoc-env  # para crear el entorno virtual, armado con Python3.9
source rastoc-env/bin/activate  # para activar el entorno
pip install -r requirements.txt  # para instalar las dependencias
```

Armar los heatmaps de un experimento:
```python
python src/data-analysis/main.py data/lectura.json
```

## Utilización

Para la utilización en navegador deben instalarse las dependencias y debe
realizarse un build como se indica en la sección anterior. Hecho esto se puede
copiar el javascript necesario (los directorios `vendor` y `build`) a donde se
lo necesite.

Al margen de si se utiliza Rastoc con su interfaz JSPsych o directamente, debe
envolverse su uso en un listener para el evento `rastoc:ready`:
```javascript
document.addEventListener('rastoc:ready', () => {
  //
})
```

### Interfaz JSPsych

Se provee una interfaz para la utilización de Rastoc a la par de JSPsych. El
experimento de lectura ([`html`](/experimentos/lectura.html),
[`js`](/experimentos/lectura.js)) puede utilizarse como referencia.  
Resumidamente, se debe:
- importar los scripts necesarios
- llamar a `jsPsych.init` dentro del handler para el evento `rastoc-ready`
- agregar los llamados a los plugins provistos `rastoc-initialize` y
`rastoc-finish`.
- agregar a WebGazer como extensión.
- realizar un llamado a `convertToTrackedTimeline` al timeline que queramos
decorar. Esta función retornará un nuevo timeline que incluye calibración del
sistema, detección de descalibración y exportación de datos en formato
estandarizado. Adicionalmente, en el último nodo del timeline input se puede 
proveer información sobre el trial ejecutado utilizando 
[`on_finish`](https://www.jspsych.org/7.0/overview/events/#on_finish-trial) y
haciendo `data.trial = { config: { ... } }`.

Scripts a importar:
```html
<script src="https://unpkg.com/@tensorflow/tfjs-core@2.4.0/dist/tf-core.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-converter@2.4.0/dist/tf-converter.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-backend-webgl@2.4.0/dist/tf-backend-webgl.js"></script>
<script src="https://unpkg.com/@tensorflow-models/face-landmarks-detection@0.0.1/dist/face-landmarks-detection.js"></script>

<link  href="../vendor/jspsych-6.3.1/css/jspsych.css" rel="stylesheet" type="text/css">
<script src="../vendor/jspsych-6.3.1/jspsych.js"></script>
<script src="../vendor/webgazer-jspsych-6.3.1/webgazer.js"></script>
<script src="../vendor/jspsych-6.3.1/extensions/jspsych-ext-webgazer.js"></script>

<script src="../build/rastoc.js"></script>
<script src="../build/rastoc-jspsych.js"></script>
```

### Utilización directa

A continuación se detalla cómo utilizar Rastoc directamente. Para referencia
puede utilizarse la implementación de
[rastoc-jspsych.js](/src/rastoc-jspsych/index.js).

Se distinguen explícitamente las fases de calibración y de estimación. Para
entrar en cada fase puede utilizarse
`const calibrator = await rastoc.switchTo.calibrating()` o 
`const { visualizer } = await rastoc.switchTo.estimating()` según corresponda.
Para pasar de una fase a otra debe primero pasarse a la fase `idle` utilizando
`rastoc.switchTo.idle()`. Puede también utilizarse
`rastoc.continueTo.estimate()` si no se desea volver a la fase `idle` pero se
desea recuperar nuevamente el objeto `visualizer`.

El objeto `calibrator` provee el método
`await calibrator.runExplicitCalibration()` que dibuja estímulos para la
calibración del sistema.  
El objeto `visualizer` provee los métodos `visualizer.showGazeEstimation()` y
`visualizer.hideGazeEstimation()` para mostrar y ocultar dónde se estima que el
sujeto está mirando.

Se informa luego lo que vaya ocurriendo gracias a
[eventos custom de javascript](https://developer.mozilla.org/en-US/docs/Web/Events/Creating_and_triggering_events#adding_custom_data_%E2%80%93_customevent).
Estos se agrupan en tres categorías: `rastoc:gaze-estimated`,
`rastoc:calibration` y `rastoc:decalibration`. Estos eventos se emiten al
elemento `document` por lo que uno puede suscribirse a ellos haciendo por
ejemplo:
```javascript
document.addEventListener('rastoc:gaze-estimated', ({ detail: gazeEvent }) => {
  // guardar la estimación en algún lado
})
```

Scripts a importar:
```html
<script src="https://unpkg.com/@tensorflow/tfjs-core@2.4.0/dist/tf-core.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-converter@2.4.0/dist/tf-converter.js"></script>
<script src="https://unpkg.com/@tensorflow/tfjs-backend-webgl@2.4.0/dist/tf-backend-webgl.js"></script>
<script src="https://unpkg.com/@tensorflow-models/face-landmarks-detection@0.0.1/dist/face-landmarks-detection.js"></script>

<script>
  jsPsych = { extensions: {} };
</script>
<script src="../vendor/webgazer-jspsych-6.3.1/webgazer.js"></script>
<script src="../vendor/jspsych-6.3.1/extensions/jspsych-ext-webgazer.js"></script>

<script src="../build/rastoc.js"></script>
```

## Investigación

En la carpeta [`/notas`](/notas/README.md) se encuentra un markdown en estilo
informe que documenta algunas ideas relacionadas al trabajo. Hay también notas
menos formales de algunos papers relacionados.
