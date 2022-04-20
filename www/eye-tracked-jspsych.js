const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('json','eye-tracked-jspsych.json');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

jsPsych.run([{
  type: jsPsychWebgazerInitCamera,
},
{
  type: rastocJSPsych.EventsTrackingStart,
},
rastocJSPsych.ensureCalibration({
  calibrationType: "assisted",
  performValidation: true,
  maxRetries: 1,
}),
{
  on_start() {
    rastoc.showGazeEstimation();
  },
  type: jsPsychHtmlButtonResponse,
  stimulus: "bla",
  choices: ['Continue'],
  on_finish() {
    rastoc.hideGazeEstimation();
  },
},
rastocJSPsych.calibrateAssistedly(),
{
  on_start() {
    rastoc.showGazeEstimation();
  },
  type: jsPsychHtmlButtonResponse,
  stimulus: "bla",
  choices: ['Continue'],
  on_finish() {
    rastoc.hideGazeEstimation();
  },
},
rastocJSPsych.calibrateFreely(),
{
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
  timeline: [rastocJSPsych.ensureCalibration({ calibrationType: "free" }), {
    type: jsPsychPsychophysics,
    on_start() {
      rastoc.showGazeEstimation();
    },
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
    extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
    on_finish() {
      rastoc.hideGazeEstimation();
    },
  }],
  repetitions: 10,
},
{
  type: rastocJSPsych.EventsTrackingStop,
},
]);
