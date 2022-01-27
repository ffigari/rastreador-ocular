const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('json','eye-tracked-jspsych.json');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

// TODO: Hardware check should be done
//       https://www.jspsych.org/7.1/plugins/browser-check/
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
