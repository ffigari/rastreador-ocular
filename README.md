# rastreador-ocular

Rastoc is a study of browser based eye tracking's applicability to remote
clinical studies.
It built up under the guidance of 
[Juan Kamienkowski](https://liaa.dc.uba.ar/juan-kamienkowski/),
[Gustavo Juantorena](https://liaa.dc.uba.ar/gustavo-juantorena-en/) and
[Bruno Bianchi](https://liaa.dc.uba.ar/bruno-bianchi-en/), in the
context of the [Scholarships for Initiation to Computer Science
Research](https://icc.fcen.uba.ar/un-primer-acercamiento-a-la-investigacion/)
provided by Buenos Aires's [Institute of Computer
Science](https://icc.fcen.uba.ar/).

A [personal fork](https://github.com/ffigari/WebGazer) of
[WebGazer](https://webgazer.cs.brown.edu/) is used for facemesh data and gaze
estimation.
Originally this package [proved to be unreliable for long sessions](
https://github.com/brownhci/WebGazer/issues/171
) but we were able to [diagnose the underlying issue and get it fixed](
https://github.com/jspsych/jsPsych/discussions/2490
).
A simple appearance based heuristic is provided to decide when the tool gets
decalibrated.  
An interface for compatiblity with [JSPsych](https://www.jspsych.org/7.1/) was
built, which relies on
[psychophysics](https://jspsychophysics.hes.kyushu-u.ac.jp/) for stimulus
drawing.
It provides utilities for calibration and decalibration detection.
This can for example be useful if you need to run multiples trials of a short
task while guaranteeing some sort of re-calibration mechanism along the way.  
By building the js (see below) and opening the `./www/index.html` file in your
browser, you should be able to play around with a couple of ready to run
examples.  
Feel free to mess around with the repo.
The issues' section is open in case you have any question or want to report a
bug.

This project was built around the antisaccades task (Hallett 1978) in which
only center, left and right over an horizontal axis are of interest.
Because of that the provided JSPsych utilities for calibration and validation
focus on those three regions of interests.
Tasks which require other regions of interest will have incorrect estimations.
Work could however be done to generalize how regions of interest are codified,
allowing then for more general calibration and validation mechanisms.

Informal experiments have shown poor quality for the estimates obtained with
this implementation as well as low (< 30 Hz) sampling rate.
[This Twitter
thread](https://twitter.com/_HanZhang_/status/1527762360076738560?t=vGxUz4ZdUnmzFq4O2GFUIw&s=08)
by Han Zhang has more details.

The resulting sampling rate also varies per subject, most probably due to 
differences in the hardware where is it run.

![sampling rates distribution](/static/second-sampling-frequencies-distribution.png)

Estimates have also shown to be shifted to one side of the screen by
potentially multiple pixels.

![shifted estimates](/static/skewed-estimations-examples.png)

This shift is consistent per session and does not happen in every session.
Information can still be retrieved in subsequent analyzes if only relative
positions of the estimates are needed, as it happen with the antisaccades task.

In our analysis small saccades were missed, due to how the saccades detection
was implemented.
For the antisaccades task this causes higher than expected correctness rates,
since small initial reflexive saccades are not detected.

![undetected saccades](/static/undetected-saccades-examples.png)

In the directory `/static` you can find plots generated with the data obtained
through both experimentation instances.
The data itself is not available.

## Usage

### Eye tracker

Node 14 is recommended.
You can set it up manually or use [`nvm`](https://github.com/nvm-sh/nvm) since
a `.nvmrc` file is provided.
Run `./install.sh` to install dependencies.  
Use `node builder.js build` to build the client side js, or use
`node builder.js watch` to build on each change.

After building, if you open `www/index.html` at your browser, you will find the
antisaccades experiment, a playgroud for the eye tracker and another one for
the jspsych interface.
There _might_ be some events' timing issues which prevent the eye tracker's
playground from starting up some times.

### Modifying the gaze estimation algorithms

Gaze estimation and eyes localization are made inside [webgazer's
fork](https://github.com/ffigari/WebGazer).
Gaze estimation is provided through a custom algorithm and eyes localization is
done by using the face landmarks detection v1.0.2 (also called facemesh) of
tfjs.
The documentation of the latter is found
[here](https://github.com/tensorflow/tfjs-models/blob/master/face-landmarks-detection/README.md#how-to-run-it).

After running the `./install.sh` script the repo will have been cloned at 
`./eye-tracker/webgazer/`.
If you want to experiment with it you will need to recompile it.
To achieve that, go to that directory, run `npm run build` to recompile and
then run `cp dist/webgazer.js ../../www/vendor` to copy the result to the place
needed by rastoc.

### Experimentation / Report

Python env setup:
```sh
python -m venv py-env
source py-env/bin/activate
pip install -r requirements.txt
```  
then `source py-env/bin/activate` each time you want to use it.

Available scripts:
```
python data-analysis/main.py display saccades-detection
python data-analysis/main.py display subjects-trials
python data-analysis/main.py display single-trial-saccades-detection 44 88
python data-analysis/main.py build informe
```
