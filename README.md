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

This project was built around the antisaccades task (Hallett 1978) in which
only center, left and right over an horizontal axis are of interest. Because of
that the provided JSPsych utilities for calibration and validation focus on
those three regions of interests. In this sense, tasks which require other
regions of interest might have their estimations worsened. Work could however
be done to generalize how regions of interest are codified, allowing then for
more general calibration and validation mechanisms.

## Development

Node 14 is recommended.
You can set it up manually or use [`nvm`](https://github.com/nvm-sh/nvm) since a
`.nvmrc` file is provided.
Then run `./install.sh` to install dependencies.  
Run `node index.js` for build instructions.
The project's entry point is situated at `www/index.html`.
You can for example open it with `firefox www/index.html`.
At `src/rastoc/` and `src/rastoc-jspsych/` you can find the entry points of the
main code.
There _might_ be some events' timing issues which prevent the playground from
starting up some times.

To setup Python env:
```sh
python -m venv py-env
source py-env/bin/activate
pip install -r requirements.txt
```  
`src/short-antisaccades-results/` contains a couple of scripts which plot the
analysis of the obtained data.
To run them, enable the python env and then use
`python src/short-antisaccades-results/<script>`.

### Old facemesh

At `./src/experimental/old-facemesh-behavior/` you can find a couple of
screenshots of the obtained bounding box with the old facemesh model.
While switching to TFJS' suggested model, it was aimed to obtain the same bbox
shape.
You can consult the consult the keypoints indexes in [their mesh map](
https://github.com/tensorflow/tfjs-models/blob/118d4727197d4a21e2d4691e134a7bc30d90deee/face-landmarks-detection/mesh_map.jpg
)

Different versions of tensorflowjs conflicts with each other even if not
imported on the same file.
To load the old model run:
```bash
npm r \
  @tensorflow-models/face-landmarks-detection \
  @tensorflow/tfjs-backend-webgl \
  @tensorflow/tfjs-converter \
  @tensorflow/tfjs-core
npm i \
  wg-tfjs@npm:@tensorflow/tfjs@2.0.1 \
  wg-tf-facemesh@npm:@tensorflow-models/facemesh@0.0.3
```
, comment out `'new-facemesh'` entry and uncomment the `'old-facemesh'` entry in
the webpack config at `./index.js`.

When finished, run:
```
npm r \
  wg-tfjs \
  wg-tf-facemesh
npm i \
  @tensorflow-models/face-landmarks-detection \
  @tensorflow/tfjs-backend-webgl \
  @tensorflow/tfjs-converter \
  @tensorflow/tfjs-core
```
and switch the comments back in the webpack config.
