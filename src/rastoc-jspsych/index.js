import { Point } from '../types/index.js';
import { shuffle } from '../utils.js';

const getPsychophysicsCanvasCenter = () => {
  // This assumes the canvas is always present. Note that if you run multiple
  // psychophysics stimulus in the same jspsych trial, then the canvas will be a
  // different one each time.
  const psychophysicsCanvas = document.getElementById('myCanvas');
  if (!psychophysicsCanvas) {
    // Canvas is not yet present
    throw new Error('psychophysics canvas not found.');
  }
  const { left, top } = psychophysicsCanvas.getBoundingClientRect();
  const { width, height } = psychophysicsCanvas;
  
  // And this assumes the canvas has not been scaled
  const x = Math.round(left + (width / 2));
  const y = Math.round(top + (height / 2));
  return new Point(x, y);
}

class EventsTrackingStart {
  static info = {
    name: 'events-tracking-start',
    parameters: {},
  }
  constructor(jsPsych) {
    this.jsPsych = jsPsych;
  }
  trial() {
    rastoc.startTrackingEvents();
    jsPsych.finishTrial({
      jspsych_start_time: this.jsPsych.getStartTime().toISOString(),
    })
  }
}

class EventsTrackingStop {
  static info = {
    name: 'events-tracking-stop',
    parameters: {},
  }
  constructor(jsPsych) {
    this.jsPsych = jsPsych;
  }
  trial() {
    jsPsych.finishTrial({
      events: rastoc.stopTrackingEvents(),
    });
  }
}

const calibrateAssistedly = () => {
  // Coordinates of calibration stimulus are codified with respect to the center
  // of the screen and are relative to the size of the viewport. Note that this
  // last part is not consistent with related bibliography where usually
  // stimulus positions are defined based in viewing angles.
  const calibrationSteps = shuffle([
    // First visit the borders of the viewport
    [- 6, - 6],
    [  0, - 6],
    [  6, - 6],
    [- 6,   0],
    [  6,   0],
    [- 6,   6],
    [  0,   6],
    [  6,   6],
  ].concat(...(
    // ...and then particularly visit each region of interest in the horizontal
    // middle line
    [0, - 4, 4].map((x) => ([
      [x    ,   0],
      [x    , - 1],
      [x    ,   1],
      [x - 1,   0],
      [x + 1,   0],
    ]))
  )).map(([x, y]) => new Point(x, y)))
  const widthDelta = () => Math.round((1 / 7) * (window.innerWidth / 2));
  const heightDelta = () => Math.round((1 / 7) * (window.innerHeight / 2));
  let calibrationPointsCount = 0;
  let mapCoordinateToGaze;
  return {
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
        <h3>Calibración asistida</h3>
        <p>
          En la próxima pantalla van a aparecer una serie de círculos. Cada vez
          que aparezca uno, fijá la mirada en él y luego presioná la barra de 
          espacio mientras seguís mirándolo.
        </p>
      `,
      choices: ["Continuar"],
      on_finish() {
        mapCoordinateToGaze = rastoc.startCalibrationPhase("external");
      },
    }, {
      timeline: [{
        type: jsPsychPsychophysics,
        stimuli: [{
          obj_type: 'circle',
          origin_center: true,
          fill_color: 'black',
          radius: 20,
          get startY() {
            return calibrationSteps[calibrationPointsCount].y * heightDelta();
          },
          get startX() {
            const {
              x: stepX,
              y: stepY,
            } = calibrationSteps[calibrationPointsCount];
            const x = stepX * widthDelta();
            const y = stepY * heightDelta();
            // The canvas won't be opened until after this current callback ends
            setTimeout(() => {
              let center;
              try {
                center = getPsychophysicsCanvasCenter();
              } catch (e) {
                console.error(e)
                throw new Error("Failed to store center coordinate of canvas");
              }
              const fn = ({ key }) => {
                if (key !== ' ') {
                  return;
                }
                mapCoordinateToGaze(center.add(x, y));
                document.removeEventListener('keydown', fn);
              };
              document.addEventListener('keydown', fn);
            }, 0)
            return x;
          },
          show_start_time: 200,
        }],
        response_type: 'key',
        response_start_time: 200,
        choices: [' '],
        on_finish() {
          calibrationPointsCount++;
        }
      }],
      loop_function() {
        const keep_looping =
          calibrationPointsCount < calibrationSteps.length;
        if (!keep_looping) {
          rastoc.endCalibrationPhase("external");
        }
        return keep_looping;
      },
    }],
    loop_function() {
      return !rastoc.isCorrectlyCalibrated;
    },
  }
}

// Calibrate system by clicking freely over the screen and until space is
// pressed.
const calibrateFreely = () => {
  return {
    timeline: [{
      type: jsPsychHtmlKeyboardResponse,
      choices: [' '],
      stimulus: `
        <div>
          <h3>Free calibration</h3>
          <p>
            On the next screen you will be allowed to freely calibrate WebGazer.
            Each click you make will map your gaze to the coordinate of the
            click. <br>
            As many times as you want, stare at your cursor and perform a click. Do
            this in the regions of the screen you want WebGazer to estimate your
            gaze.
          </p>
          <p>
            You will be shown the gaze estimation while you add calibration
            points. Press <i>Space</i> to start. When you are satisfied press
            <i>Space</i> again to finish the calibration process.
          </p>
        </div>
        `,
      on_finish() {
        rastoc.startCalibrationPhase("click");
      },
    }, {
      type: jsPsychHtmlKeyboardResponse,
      choices: [' '],
      stimulus: '',
      on_finish() {
        rastoc.endCalibrationPhase("click");
      },
    }],
    loop_function() {
      return !rastoc.isCorrectlyCalibrated;
    },
  };
};

// Validates current calibration by checking relative positioning of
// estimations.
const validateCalibration = () => {
  const widthDelta = () => 2 * window.innerWidth / 6;
  const heightDelta  = () => 2 * window.innerHeight / 6;
  let steps, stepsIdx, x, y, results;
  return {
    on_timeline_start() {
      results = []
      stepsIdx = 0;
      steps = [
        [0, 0],
        ...shuffle([
          [-1, -1],
          [-1,  1],
          [ 1, -1],
          [ 1,  1],
        ]),
        [ 0,  0],
      ].map(([x, y]) => new Point(x, y))
      rastoc.showGazeEstimation();
    },
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
        <h3>Validación</h3>
        <p>
          En la próxima pantalla van a aparecer una serie de círculos. Cada vez
          que aparezca uno, fijá la mirada en él y luego presioná la barra de 
          espacio mientras seguís mirándolo.
        </p>
      `,
      choices: ["Continuar"],
    }, {
      timeline: [{
        type: jsPsychPsychophysics,
        stimuli: [{
          obj_type: 'circle',
          origin_center: true,
          fill_color: 'blue',
          radius: 20,
          get startX() {
            return steps[stepsIdx].x * widthDelta();
          },
          get startY() {
            return steps[stepsIdx].y * heightDelta();
          },
          show_start_time: 200,
        }],
        response_type: 'key',
        response_start_time: 200,
        choices: [' '],
        extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
        on_finish(data) {
          const lastEstimations = data.webgazer_data.filter(({
            t
          }) => data.rt - 300 < t && t < data.rt)
          results.push({
            xStep: steps[stepsIdx].x,
            yStep: steps[stepsIdx].y,
            lastEstimations,
          });
          stepsIdx++;
        }
      }],
      loop_function() {
        return stepsIdx < steps.length;
      },
    }],
    on_timeline_finish() {
      results = results.map(r => {
        const [avgX, avgY] = ['x', 'y'].map((
          axis
        ) => {
          const values = r.lastEstimations.map((e) => e[axis])
          const total = values.reduce((acc, cur) => acc + cur);
          return total / values.length;
        })
        r.avgX = avgX;
        r.avgY = avgY;
        return r;
      })

      const firstCenter = results[0];
      const lastCenter = results[results.length - 1];
      const centersCoincide = 
        Math.abs(firstCenter.avgX - lastCenter.avgX) < 100 &&
        Math.abs(firstCenter.avgY - lastCenter.avgY) < 100;

      const validationSucceded =
        centersCoincide;

      jsPsych.data.get().addToLast({
        type: 'validation-results',
        // TODO: Store metrics about estimates
        validationSucceded,
      })
      rastoc.hideGazeEstimation();
    },
  }
}

// If the system is not calibrated, loops over calibration node until system is
// calibrated. Optionally, perform a validation after calibrating.
const ensureCalibration = (options) => {
  options = options || {};
  options.calibrationType = options.calibrationType || "assisted";
  options.performValidation = options.performValidation || false;

  let unsucessfulCalibration = false;
  const body = [{
    conditional_function() {
      return unsucessfulCalibration;
    },
    timeline: [{
      type: jsPsychHtmlKeyboardResponse,
      stimulus: "Hubo un problema con la última calibración, reintentando.",
      choices: "NO_KEYS",
      trial_duration: 2000,
    }],
  }];
  if (options.calibrationType === "assisted") {
    body.push(calibrateAssistedly());
  } else if (options.calibrationType === "free") {
    body.push(calibrateFreely());
  } else {
    throw new Error(`Unrecognized calibrationType=${options.calibrationType}`);
  }
  if (options.performValidation) {
    body.push(validateCalibration());
  }

  return {
    conditional_function() {
      return !rastoc.isCorrectlyCalibrated;
    },
    timeline: [{
      type: jsPsychHtmlKeyboardResponse,
      stimulus: "Descalibración detectada",
      choices: "NO_KEYS",
      trial_duration: 2000,
    }, {
      timeline: body,
      loop_function() {
        unsucessfulCalibration = !rastoc.isCorrectlyCalibrated;
        if (options.performValidation) {
          const validations = jsPsych.data.get().trials.filter((
            x
          ) => x.type === 'validation-results')
          const lastValidation = validations[validations.length - 1];
          unsucessfulCalibration =
            unsucessfulCalibration || !lastValidation.validationSucceded;
        };
        return unsucessfulCalibration;
      },
    }],
  }
}


window.rastocJSPsych = {
  EventsTrackingStart,
  EventsTrackingStop,
  calibrateAssistedly,
  calibrateFreely,
  ensureCalibration,
};

