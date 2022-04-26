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

const quarterOfVerticalSpace = () => Math.round((1 / 4) * window.innerHeight);
const sixthOfVerticalSpace = () => Math.round((1 / 6) * window.innerHeight)
const thirdOfHorizontalSpace = () => Math.round((1 / 3) * window.innerWidth);
const quarterOfHorizontalSpace = () => Math.round((1 / 4) * window.innerWidth);

// Region of interest is now hardcoded to this 3 xs coordinates below since only
// horizontal coordinates are relevant for the antisaccades task.
// Positions of calibration stimulus are specified in pixels. This goes against
// what's mostly found in the bibliography, where distances are usually defined
// in degrees.
const interestRegionsXs = () => [
  0,
  - thirdOfHorizontalSpace(),
  thirdOfHorizontalSpace()
]

let calibrationId = 0
const calibrateAssistedly = () => {
  let calibrationPointsCount, calibrationStimulusCoordinates;
  let mapCoordinateToGaze;
  return {
    on_timeline_start() {
      calibrationPointsCount = 0;
      calibrationStimulusCoordinates = [
        new Point(0, - quarterOfVerticalSpace()),
        new Point(0, quarterOfVerticalSpace()),
      ];
      shuffle([
        0,
        - quarterOfHorizontalSpace() / 4,
        quarterOfHorizontalSpace() / 4,
      ]).forEach((
        d
      ) => interestRegionsXs().forEach((
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
        on_finish(data) {
          data["rastoc-type"] = "calibration-stimulus";
          data["stimulus-coordinate"] = {
            x: calibrationStimulusCoordinates[calibrationPointsCount].x,
            y: calibrationStimulusCoordinates[calibrationPointsCount].y,
          };
          data["calibration-id"] = calibrationId
          data["calibration-point-id"] = calibrationPointsCount;
          data["inner-width"] = window.innerWidth;
          data["inner-height"] = window.innerHeight;
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
    on_timeline_finish() {
      calibrationId++;
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
let validationId = 0;
const validateCalibration = () => {
  let validationPointsCount, validationStimulusCoordinates;
  return {
    on_timeline_start() {
      validationPointsCount = 0;
      validationStimulusCoordinates = [];
      [
        sixthOfVerticalSpace(),
        - sixthOfVerticalSpace()
      ].forEach((
        y
      ) => interestRegionsXs().forEach((
        x
      ) => validationStimulusCoordinates.push(new Point(x, y))));
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
            return validationStimulusCoordinates[validationPointsCount].x;
          },
          get startY() {
            return validationStimulusCoordinates[validationPointsCount].y;
          },
          show_start_time: 50,
          show_end_time: 750,
        }, {
          obj_type: 'circle',
          origin_center: true,
          fill_color: 'black',
          radius: 20,
          get startX() {
            return validationStimulusCoordinates[validationPointsCount].x;
          },
          get startY() {
            return validationStimulusCoordinates[validationPointsCount].y;
          },
          show_start_time: 750,
        }],
        response_type: 'key',
        response_start_time: 750,
        choices: [' '],
        extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
        on_finish(data) {
          data["rastoc-type"] = "validation-stimulus";
          data["stimulus-coordinate"] = {
            x: validationStimulusCoordinates[validationPointsCount].x,
            y: validationStimulusCoordinates[validationPointsCount].y,
          };
          data["validation-id"] = validationId
          data["validation-point-id"] = validationPointsCount;
          data["last-estimations"] = data.webgazer_data.filter(({
            t
          }) => data.rt - 250 < t && t < data.rt)
          data["inner-width"] = window.innerWidth;
          data["inner-height"] = window.innerHeight;
          validationPointsCount++;
        }
      }],
      loop_function() {
        return validationPointsCount < validationStimulusCoordinates.length;
      },
    }],
    on_timeline_finish() {
      const results = jsPsych.data.get().trials.filter((
        t
      ) => t["rastoc-type"] === "validation-stimulus" && t["validation-id"] === validationId);

      let relativePositionsAreCorrect = true;
      const avgX = (r) => (r['last-estimations'].reduce((
        acc, { x }
      ) => acc + x, 0)) / r['last-estimations'].length;
      results.forEach((r1, i) => results.forEach((r2, j) => {
        if (j <= i) {
          return;
        }
        const r1X = r1["stimulus-coordinate"].x;
        const r2X = r2["stimulus-coordinate"].x;
        if (r1X === r2X) {
          return;
        }

        const r1AvgX = avgX(r1);
        const r2AvgX = avgX(r2);
        let pairHasCorrectPosition;
        if (r1X > r2X) {
          pairHasCorrectPosition = r1AvgX > r2AvgX;
        } else {
          pairHasCorrectPosition = r1AvgX < r2AvgX;
        }
        if (!pairHasCorrectPosition) {
          console.warn("Incorrect relative position detected", r1, r2);
        }
        relativePositionsAreCorrect =
          relativePositionsAreCorrect && pairHasCorrectPosition;
      }))
      jsPsych.data.get().addToLast({
        "validation-results": {
          relativePositionsAreCorrect
        },
      });
      validationId++;
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
          const validationsResults = jsPsych.data.get().trials.filter((
            x
          ) => x["rastoc-type"] === 'validation-stimulus' && !!x["validation-results"]);
          const lastValidation =
            validationsResults[validationsResults.length - 1];
          unsucessfulCalibration = unsucessfulCalibration ||
            !lastValidation["validation-results"].relativePositionsAreCorrect;
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

