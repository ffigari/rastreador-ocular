// TODO: The rastoc-finalize plugin should export calibration events, detection
//       of decalibration events and the evolution confidence measure
// TODO: Check how to match js Date timestamps against JSP "time_elapsed" values
const handler = ({ clientX, clientY }) => {
  rastoc.mapCoordinateToGaze(clientX, clientY);
};
window.rastocJSPsych = {
  createFreeCalibrationNode: () => {
    return { timeline: [{
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
        rastoc.resetCalibration();
        webgazer.resume();
        webgazer.showPredictionPoints(true);
        document.addEventListener('click', handler);
      },
    }, {
      type: jsPsychHtmlKeyboardResponse,
      choices: [' '],
      stimulus: '',
      on_finish() {
        document.removeEventListener('click', handler);
        webgazer.showPredictionPoints(false);
      },
    }]};
  }
};

