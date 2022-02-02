# rastreador-ocular

## Development

Run `node index.js` for build instructions.
Check node version at `.nvmrc`.

## Next steps

#### Add confidence metric back

A confidence metric should be provided.
Low values should correlate with good estimations.  
Ideally it could go directly inside the data added by the WG extension.
It could also be exported at the end inside a big array.

Code from before:
```
// La medida de confianza es una exponencial inversa en función de
// la distancia promedio de los ojos a las posiciones válidas.
// f(0)  = 1
// f(5)  = 0.368
// f(10) = 0.135
const confidence = Math.pow(
  Math.E,
  - movementDetector.distanceToValidPosition() / 5
);
document.dispatchEvent(new CustomEvent('rastoc:gaze-estimated', {
  detail: {
    name: 'gaze-estimation',
    ts: new Date,
    x: prediction.x,
    y: prediction.y,
    confidence,
  },
}))
```

#### Export rastoc events

The history of each run should be "rebuildable".
For this events like calibrations or met decalibration checks should be
exported.

#### Plot experiment's history

Plotting the history of a run would allow to check the exported events make
sense.

#### Check user's system config

Ensure the user meets some minimum reqirements about hardware.

```
  if (cameraIsAccessible) {
    try {
      const userMedia = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          width: { min: MINIMUM_CAMERA_WIDTH },
          height: { min: MINIMUM_CAMERA_HEIGHT },
        },
      });
      const videoSettings = userMedia.getVideoTracks()[0].getSettings()
      systemConfig.cameraWidth = videoSettings.width
      systemConfig.cameraHeight = videoSettings.height
    } catch (e) {
      errors.push(
        `Tu cámara web no tiene la resolución mínima necesaria de ${
          MINIMUM_CAMERA_WIDTH
        }x${
          MINIMUM_CAMERA_HEIGHT
        }.`
      );
    }
  }
```

#### Add support for virtual-chinrest plugin

In neuro research it seems to be common to report the angles of the shown
stimulus.
Pixels values aren't usually reported.
To allow for angle dependant calibrations, support for the 'virtual-chinrest'
plugin should be added.
This way the 'pixels to degrees' ratio will be available.

## Utilización

Se provee una interfaz JSPsych para utilizar Rastoc. El
experimento de antisacadas ([`html`](/experimentos/online-experiment.html),
[`js`](/experimentos/online-experiment.js)) puede utilizarse como referencia.  
Resumidamente, se debe:
- importar los scripts necesarios (listados abajo)
- llamar a `jsPsych.init` dentro de un listener para el evento `rastoc-ready`:
```javascript
document.addEventListener('rastoc:ready', () => {
  jsPsych.init(...);
})
```
- agregar los llamados a los plugins `webgazer-init-camera`, `rastoc-initialize`
y `rastoc-finish`.
- agregar a WebGazer como extensión.

#### Scripts a importar

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

## Investigación

En la carpeta [`/notas`](/notas/README.md) se encuentra un markdown en estilo
informe que documenta algunas ideas relacionadas al trabajo. Hay también notas
menos formales de algunos papers relacionados.  
A partir de un momento las notas las fui subiendo a un drive.
