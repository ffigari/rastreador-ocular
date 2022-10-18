const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('csv', 'precision-experiment.csv');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

let validationStimulusCoordinates;
let idx;
const instancesPerExperiment = 3; // 10;
const trialsPerInstance = 3; // 10;

jsPsych.run([{
  type: jsPsychSurveyHtmlForm,
  preamble: `
    <h3> Precision Experiment </p>
  `,
  html: `
    The following experiment will help establish metrics about the quality of
    our system's gaze estimations and about its degradation over time.
    <br>

    ${instancesPerExperiment} times you will calibrate the system and perform a
    simple non-interactive task.
    <br>
    <br>

    Please complete the data below:
    <br>

    <label for="web-browser">Web Browser</label>
    <input type="text" name="web-browser" id="web-browser-input">
    <br>

    <label for="operating-system">Operating System</label>
    <input type="text" name="operating-system" id="operating-system-input">
    <br>

    <label for="webcam">Webcam</label>
    <input type="text" name="webcam" id="webcam-input"
      placeholder="brand, frame rate, resolution, ..."
    >
    <br>
    <br>
  `,
}, {
  type: jsPsychWebgazerInitCamera,
}, {
  type: rastocJSPsych.EventsTrackingStart,
}, {
  type: jsPsychVirtualChinrest,
}, {
  repetitions: instancesPerExperiment,
  timeline: [rastocJSPsych.calibrate.assistedly("fullscreen"), {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
      <h4>Experimentation Session</h4>

      ${trialsPerInstance} times you will see a series of stimulus in the same
      positions in which you just calibrated.
      Fix your gaze on them as they appear.
      <br>

      A central cross will appear in between each pair of series.
      While this cross is present you can rest your gaze and blink.
      <br>

      Press the space bar to start.
        `,
    choices: [' '],

  }, {
    repetitions: trialsPerInstance,
    timeline: [{
      type: jsPsychPsychophysics,
      background_color: '#d3d3d3',
      stimuli: [{
        obj_type: 'cross',
        origin_center: true,
        startX: 0,
        startY: 0,
        show_start_time: 100,
        show_end_time: 1900,
        line_length: 40,
      }],
      response_ends_trial: false,
      trial_duration: 2000,
      extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
      on_finish(data) {
        data["rastoc-type"] = "tracked-stimulus";
        data["trial-tag"] = "fixation-stimulus";
        data["start-x"] = 0;
        data["start-y"] = 0;
        validationStimulusCoordinates = 
          rastocJSPsych.getCalibrationStimulusCoordinates();
        idx = 0;
      },
    }, {
      timeline: [{
        type: jsPsychPsychophysics,
        background_color: '#d3d3d3',
        stimuli: [{
          obj_type: 'circle',
          origin_center: true,
          get startX() {
            return validationStimulusCoordinates[idx].x;
          },
          get startY() {
            return validationStimulusCoordinates[idx].y
          },
          show_start_time: 0,
          show_end_time: 1000,
          radius: 20,
          line_color: 'black',
          fill_color: 'black',
        }],
        response_ends_trial: false,
        trial_duration: 1000,
        extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
        on_finish(data) {
          data["rastoc-type"] = "tracked-stimulus";
          data["trial-tag"] = "validation-stimulus";
          data["start-x"] = validationStimulusCoordinates[idx].x;
          data["start-y"] = validationStimulusCoordinates[idx].y;
        },
      }],
      loop_function() {
        idx++;
        return idx < validationStimulusCoordinates.length;
      },
    }],
  }],
}, {
  type: rastocJSPsych.EventsTrackingStop,
}])
