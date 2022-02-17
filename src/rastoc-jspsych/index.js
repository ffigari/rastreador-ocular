import { Point } from '../types/index.js';

const getPsychophysiscCanvasCenter = () => {
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
  const totalCalibrationPoints = 9;
  let calibrationPointsCount = 0;
  let mapCoordinateToGaze;
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
          radius: 20,
          origin_center: true,
          fill_color: 'blue',
          get startX() {
            const x = Math.round((
              Math.random() < 0.5 ? 1 : -1
            ) * (
              Math.random() * (window.innerWidth / 2 - 20)
            ))
            const y = 0;
            // The canvas won't be opened until after this runs...
            setTimeout(() => {
              let center;
              try {
                center = getPsychophysiscCanvasCenter();
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
          startY: 0,
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
        const keep_looping = calibrationPointsCount < totalCalibrationPoints
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

