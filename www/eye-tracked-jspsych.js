// TODO: Move this to '/src/rastoc.js' so that I can use it in the rastoc
//       playground
// TODO: Subscribe to WG's eye patches update and draw them over the debugging
//       canvas that has the video
// TODO: Reimplement movement detection by reusing WG eye patches
const rastoc = {
  resetCalibration() {
    // TODO: Reset movement detection data
    webgazer.clearData();
  },
  mapCoordinateToGaze(x, y) {
    // TODO: Add gaze position as valid position
    webgazer.recordScreenPosition(x, y, 'click');
  },
};

// TODO: The rastoc-finalize plugin should export calibration events, detection
//       of decalibration events and the evolution confidence measure
// TODO: Check how to match js Date timestamps against JSP "time_elapsed" values
const handler = ({ clientX, clientY }) => {
  rastoc.mapCoordinateToGaze(clientX, clientY);
};
const rastocJSPsych = {
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

const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('json','eye-tracked-jspsych.json');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

// TODO: Add usage of virtual-chinrest plugin to retrieve the angle of vision
//       and draw stimulus accordingly
// TODO: When movement detection is up again, replace toy task with a quick one
//       time based and ensure calibration between tasks
jsPsych.run([{
  type: jsPsychWebgazerInitCamera,
}, rastocJSPsych.createFreeCalibrationNode(), {
  type: jsPsychHtmlButtonResponse,
  stimulus: `
      <div>
        <p>
          During this screen your gaze is being estimated using JSPsych's
          WebGazer extension.
        </p>
        <p id="my-paragraph">
          The ID of this pragraph element has been passed to the <a
          href="https://www.jspsych.org/7.1/overview/eye-tracking/#adding-eye-tracking-to-a-trial">
          targets parameter</a> of the extension.
        </p>
      </div>
    `,
  extensions: [{
    type: jsPsychExtensionWebgazer, 
    params: { targets: ['#my-paragraph'] },
  }],
  choices: ["Continue"],
}]);
