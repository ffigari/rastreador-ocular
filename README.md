# rastreador-ocular

Rastoc is a study of browser based eye tracking's applicability in assisting the
diagnosis of neuropsychological conditions.
It built up from the ongoing research with
[Juan Kamienkowski](https://liaa.dc.uba.ar/juan-kamienkowski/),
[Bruno Bianchi](https://liaa.dc.uba.ar/bruno-bianchi-en/) and
[Gustavo Juantorena](https://liaa.dc.uba.ar/gustavo-juantorena-en/), who are
directing [my](https://liaa.dc.uba.ar/francisco-figari-en/) master thesis at
LIAA, UBA on the same topic.

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
A [JSPsych](https://www.jspsych.org/7.1/) interface was built, which relies on
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

## Experimentation

Python env setup:
```sh
python -m venv py-env
source py-env/bin/activate
pip install -r requirements.txt
```  

Usage:
- `python src/experimentation/informe.py`: Print report.
- `python src/experimentation/raw_data_cooker.py`: Create specific resources.
