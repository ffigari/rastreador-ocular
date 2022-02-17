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

const createSideToSideCalibrationNode = () => {
  let mapCoordinateToGaze;
  const radius = 20;
  // Coordinates of calibration stimulus are codified with respect to the center
  // of the screen and are relative to the size of the viewport. Note that this
  // last part is not consistent with related bibliography where usually
  // stimulus positions are defined based in viewing angles.
  const widthStep = Math.round((1 / 7) * (window.innerWidth / 2));
  const heightStep = Math.round((1 / 7) * (window.innerHeight / 2));
  const calibrationStimulusCoordinates = shuffle([
    // First visit the borders of the viewport
    [- 6 * widthStep, - 6 * heightStep],
    [  0            , - 6 * heightStep],
    [  6 * widthStep, - 6 * heightStep],
    [- 6 * widthStep,   0             ],
    [  6 * widthStep,   0             ],
    [- 6 * widthStep,   6 * heightStep],
    [  0            ,   6 * heightStep],
    [  6 * widthStep,   6 * heightStep],
  ].concat(...(
    // ...and then particularly visit each region of interest in the horizontal
    // middle line
    [0, - 4 * widthStep, 4 * widthStep].map((x) => ([
      [x            ,   0],
      [x            , - heightStep],
      [x            ,   heightStep],
      [x - widthStep,   0],
      [x + widthStep,   0],
    ]))
  )).map(([x, y]) => new Point(x, y)));
  let calibrationPointsCount = 0;
  return {
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <h3>
        Calibración lado a lado
      </h3>
      <p>
        En la próxima pantalla van a ir apareciendo puntos azules. Cada vez que
        aparezca uno, fijá la mirada en él y presiona la barra de espacio.
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
          radius,
          origin_center: true,
          fill_color: 'blue',
          get startX() {
            const {
              x, y
            } = calibrationStimulusCoordinates[calibrationPointsCount];
            // The canvas won't be opened until after this runs...
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
          get startY() {
            return calibrationStimulusCoordinates[calibrationPointsCount].y;
          },
          show_start_time: 400,
        }],
        response_type: 'key',
        response_start_time: 400,
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
};
const createFreeCalibrationNode = () => {
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
const createEnsuredCalibrationNode = (calibrationType) => {
  if (calibrationType === "free") {
    return createFreeCalibrationNode();
  } else if (calibrationType === "side-to-side") {
    return createSideToSideCalibrationNode();
  } else {
    throw new Error(`'${calibrationType}' is not a valid calibration type.`);
  }
};

const createCalibrationBarrierNode = (calibrationType) => {
  return {
    conditional_function() {
      return !rastoc.isCorrectlyCalibrated;
    },
    timeline: [{
      type: jsPsychHtmlKeyboardResponse,
      choices: [' '],
      stimulus: `
      <p>
        Descalibración detectada.
        Presioná <i>Espacio</i> para proceder con la calibración.
      <p>
      `,
    }, createEnsuredCalibrationNode(calibrationType)],
    loop_function() {
      return !rastoc.isCorrectlyCalibrated;
    }
  }
};

window.rastocJSPsych = {
  createEnsuredCalibrationNode,
  createCalibrationBarrierNode,
  EventsTrackingStart,
  EventsTrackingStop,
};

