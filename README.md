# rastreador-ocular

Rastoc is a study of browser based eye tracking's applicability in assisting the
diagnosis of neuropsychological conditions.
It built up from the ongoing research with
[Juan Kamienkowski](https://liaa.dc.uba.ar/juan-kamienkowski/),
[Bruno Bianchi](https://liaa.dc.uba.ar/bruno-bianchi-en/) and
[Gustavo Juantorena](https://liaa.dc.uba.ar/gustavo-juantorena-en/), who are
directing [my](https://liaa.dc.uba.ar/francisco-figari-en/) master thesis at
LIAA, UBA on the same topic.

[Webgazer](https://webgazer.cs.brown.edu/) is used for facemesh data and gaze
estimation.
At the moment, this package has proven to be unreliable, with [unexpected
crashes after a couple of minutes](
https://github.com/jspsych/jsPsych/discussions/2490).
A simple appearance based heuristic is provided to decide when the tool gets
decalibrated.  
A [JSPsych](https://www.jspsych.org/7.1/) interface was built, which relies on
[psychophysics](https://jspsychophysics.hes.kyushu-u.ac.jp/) for stimulus
drawing.
It provides a couples of assist functions to insert calibration barriers inside
JSPsych's timelines.
This can for example be useful if you need to run multiples trials of a short
task while guaranteeing some sort of re-calibration mechanism along the way.  
By building the js (see below) and opening the `./www/index.html` file in your
browser, you should be able to play around with a couple of ready to run
examples.  
Feel free to mess around with the repo.
The issues' section is open in case you have any question or want to report a
bug.

## Development

Run `./install.sh` to install dependencies.  
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

#### Plot experiment's history

Plotting the history of a run would allow to check the exported events make
sense.

#### Check user's system config

Ensure the user meets some minimum reqirements about hardware (
https://www.jspsych.org/7.1/plugins/browser-check/).


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
