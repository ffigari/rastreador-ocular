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
}, {
  timeline: [rastocJSPsych.createCalibrationBarrierNode(), {
    type: jsPsychPsychophysics,
    // TODO: Enable marker
    stimuli: [
      {
        obj_type: 'cross',
        origin_center: true,
        get startX() {
          return (Math.random() < 0.5 ? 1 : -1) * (Math.round(Math.random() * 200) + 20);
        },
        startY: 0,
        show_start_time: 100,
        show_end_time: 900,
        line_length: 40,
      },
    ],
    response_ends_trial: false,
    trial_duration: 1000,
  }],
  repetitions: 10,
}]);
