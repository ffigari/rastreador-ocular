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

// Positions of calibration stimulus are specified in pixels. This goes against
// what's mostly found in the bibliography, where distances are usually defined
// in degrees.
const calibrateAssistedly = () => {
  const verticalDelta = () => Math.round((1 / 2) * (window.innerHeight / 2));
  const horizontalDelta = () => Math.round((1 / 2) * (window.innerWidth / 2));
  let interestRegionsXs;
  let calibrationPointsCount, calibrationStimulusCoordinates;
  let mapCoordinateToGaze;
  return {
    on_timeline_start() {
      interestRegionsXs = [
        0,
        - horizontalDelta(),
        horizontalDelta()
      ];

      calibrationPointsCount = 0;
      calibrationStimulusCoordinates = [
        new Point(0, - verticalDelta()),
        new Point(0, verticalDelta()),
      ];
      shuffle([0, - horizontalDelta() / 4, horizontalDelta() / 4]).forEach((
        d
      ) => interestRegionsXs.forEach((
        x
      ) => calibrationStimulusCoordinates.push(new Point(d + x, 0))));
    },
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
        <h3>Calibración</h3>
        <p>
          Para cada punto que aparezca
        </p>
        <ol>
          <li>fijá la mirada en él</li>
          <li>esperá a que cambie de color, manteniendo fija la mirada</li>
          <li>presioná la barra de espacio</li>
        </ol>
      `,
      choices: ["Continuar"],
      on_finish() {
        mapCoordinateToGaze = rastoc.startCalibrationPhase("external");
      },
    }, {
      timeline: [{
        type: jsPsychPsychophysics,
        background_color: '#d3d3d3',
        stimuli: [{
          obj_type: 'circle',
          origin_center: true,
          fill_color: 'blue',
          radius: 20,
          get startY() {
            return calibrationStimulusCoordinates[calibrationPointsCount].y;
          },
          get startX() {
            const {
              x,
              y,
            } = calibrationStimulusCoordinates[calibrationPointsCount];
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
          show_start_time: 50,
          show_end_time: 550,
        }, {
          obj_type: 'circle',
          origin_center: true,
          fill_color: 'black',
          radius: 20,
          get startY() {
            return calibrationStimulusCoordinates[calibrationPointsCount].y;
          },
          get startX() {
            return calibrationStimulusCoordinates[calibrationPointsCount].x;
          },
          show_start_time: 550,
        }],
        response_type: 'key',
        response_start_time: 550,
        choices: [' '],
        on_finish() {
          calibrationPointsCount++;
        }
      }],
      loop_function() {
        const keep_looping =
          calibrationPointsCount < calibrationStimulusCoordinates.length;
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
    },
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
        <h3>Validación</h3>
        <p>
          Para cada punto que aparezca
        </p>
        <ol>
          <li>fijá la mirada en él</li>
          <li>esperá a que cambie de color, manteniendo fija la mirada</li>
          <li>presioná la barra de espacio</li>
        </ol>
      `,
      choices: ["Continuar"],
    }, {
      timeline: [{
        type: jsPsychPsychophysics,
        background_color: '#d3d3d3',
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
          show_start_time: 50,
          show_end_time: 750,
        }, {
          obj_type: 'circle',
          origin_center: true,
          fill_color: 'black',
          radius: 20,
          get startX() {
            return steps[stepsIdx].x * widthDelta();
          },
          get startY() {
            return steps[stepsIdx].y * heightDelta();
          },
          show_start_time: 750,
        }],
        response_type: 'key',
        response_start_time: 750,
        choices: [' '],
        extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
        on_finish(data) {
          const lastEstimations = data.webgazer_data.filter(({
            t
          }) => data.rt - 175 < t && t < data.rt)
          results.push({
            step: steps[stepsIdx],
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

      const topLeft  = results.find(r => r.step.x === -1 && r.step.y === -1);
      const topRight = results.find(r => r.step.x ===  1 && r.step.y === -1);
      const botLeft  = results.find(r => r.step.x === -1 && r.step.y ===  1);
      const botRight = results.find(r => r.step.x ===  1 && r.step.y ===  1);
      // To allow for smoother ux I'm validating only the X coordinate since the
      // Y coordinate is not relevant to the antisaccades tasks
      const correctRelativePositions =
        topLeft.avgX < topRight.avgX &&
        botRight.avgX > botLeft.avgX;

      const firstCenter = results[0];
      const lastCenter = results[results.length - 1];
      const centersCoincide = 
        Math.abs(firstCenter.avgX - lastCenter.avgX) < 300 &&
        Math.abs(firstCenter.avgY - lastCenter.avgY) < 300;

      const validationSucceded = centersCoincide && correctRelativePositions;

      jsPsych.data.get().addToLast({
        type: 'validation-results',
        results,
        correctRelativePositions,
        centersCoincide,
        validationSucceded,
      })
    },
  }
}

// If the system is not calibrated, loops over calibration node until system is
// calibrated. Optionally, perform a validation after calibrating.
const ensureCalibration = (options) => {
  options = options || {};
  options.calibrationType = options.calibrationType || "assisted";
  options.forceCalibration = options.forceCalibration || false;
  options.performValidation = options.performValidation || false;
  options.maxRetries = options.maxRetries || 3;

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

  let calibrationsCounts;
  return {
    conditional_function() {
      return !rastoc.isCorrectlyCalibrated || options.forceCalibration;
    },
    on_timeline_start() {
      calibrationsCounts = 0;
    },
    timeline: [{
      type: jsPsychHtmlKeyboardResponse,
      stimulus: "Calibrando",
      choices: "NO_KEYS",
      trial_duration: 2000,
    }, {
      timeline: body,
      loop_function() {
        calibrationsCounts++;

        unsucessfulCalibration = !rastoc.isCorrectlyCalibrated;
        if (options.performValidation) {
          const validations = jsPsych.data.get().trials.filter((
            x
          ) => x.type === 'validation-results');
          const lastValidation = validations[validations.length - 1];
          unsucessfulCalibration =
            unsucessfulCalibration || !lastValidation.validationSucceded;
        };
        return calibrationsCounts <= options.maxRetries && unsucessfulCalibration;
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

