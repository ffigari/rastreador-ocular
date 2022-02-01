// TODO: Export rastoc events
//         . create an object which captures rastoc events on an array and allow
//           them to be retrieved later on
//         . after each trial, add ocurred rastoc events to last trial so that
//           behavior is more consistent with the current webgazer events
// TODO: Check how to match js Date timestamps against JSP "time_elapsed" values
const createSideToSideCalibrationNode = () => {
  return {
    // TODO: Add calibration here. Here it should be triggered with the space
    //       bar. It will be needed to recover the coordinate of the calibration
    //       stimulus shown so that we can send that coordinate to webgazer
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <h3>
        Calibración lado a lado
      </h3>
      <p>
        En la próxima pantalla van a ir apareciendo puntos azules. Cada vez que
        aparezca uno, fijá la mirada en él y presiona la barra de espacio
      </p>
      `,
      choices: ["Continuar"],
    }],
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
        // TODO: Take the click mapping done for calibration outside rastoc and
        //       into here. A new method should be exposed with allows a
        //       coordinate to be mapped. Then out here 
        //       Maybe a callback that uses that method will be enough
        rastoc.startCalibrationPhase();
      },
    }, {
      type: jsPsychHtmlKeyboardResponse,
      choices: [' '],
      stimulus: '',
      on_finish() {
        // TODO: Any listener added above should be removed here
        rastoc.endCalibrationPhase();
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
        Decalibration detected.
        Press <i>Space</i> to proceed with calibration
      <p>
      `,
    }, createEnsuredCalibrationNode(calibrationType)],
    loop_function() {
      return !rastoc.isCorrectlyCalibrated;
    }
  }
};

// TODO: Add side to side calibration
//         . allow calibration method to be chosen via a parameter
window.rastocJSPsych = {
  createEnsuredCalibrationNode,
  createCalibrationBarrierNode,
};

