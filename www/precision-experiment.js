const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave(
      'csv',
      `precision-experiment-${(new Date).toISOString()}.csv`
    );
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

let validationStimulusCoordinates;
let idx;
const sessionsPerRun = 10;
const validationsPerSession = 10;

let sessionId = 0;
let validationId = 0;
let trackedTrialId = 0;
const stampIds = (data) => {
  data["session-id"] = sessionId
  data["validation-id"] = validationId
  trackedTrialId += 1
  data["tracked-trial-id"] = trackedTrialId
}

jsPsych.run([{
  type: jsPsychSurveyHtmlForm,
  preamble: ``,
  html: `
    <h2> Precision Experiment </h2>

    The following experiment will help establish metrics about the quality of
    our system's gaze estimations and about its degradation over time.
    <br>

    ${sessionsPerRun} times you will calibrate the system and perform a
    simple non-interactive task.
    <br>
    <br>

    Retrieve the ids of your computer and your webcam from <a
    href="https://docs.google.com/spreadsheets/d/1il1rCGHjaK3SnQk07awIZq2zVa5_H30TJPjoGr197jo/edit#gid=0"
    >this spreadsheet</a>.
    If necessary, add new rows.
    <br>

    Once you have that, please complete the information below.
    <br>

    <label for="webcam">Webcam id</label>
    <input required type="number" name="webcam-id" id="webcam-input">
    <br>

    <label for="computer">Computer id</label>
    <input required type="number" name="computer-id" id="computer-input">
    <br>

    <label for="web-browser">Web Browser</label>
    <input required type="text" name="web-browser" id="web-browser-input">
    <br>

    <label for="operating-system">Operating System</label>
    <input required type="text" name="operating-system" id="operating-system-input">
    <br>

    <br>
  `,
}, {
  type: jsPsychWebgazerInitCamera,
}, {
  type: jsPsychFullscreen
}, {
  type: rastocJSPsych.EventsTrackingStart,
}, {
  type: jsPsychVirtualChinrest,
}, {
  repetitions: sessionsPerRun,
  timeline: [rastocJSPsych.calibrate.assistedly("fullscreen"), {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: () => `
      <h3>Experimentation Session (${sessionId + 1} / ${sessionsPerRun})</h3>
      ${validationsPerSession} times you will see a series of stimulus in the same
      positions in which you just calibrated.
      Fix your gaze on them as they appear.
      <br>

      A central cross will appear in between each pair of series.
      While this cross is present you can rest your gaze and blink.
      <br>

      Press the space bar to start.
        `,
    choices: [' '],
    on_finish() {
      sessionId += 1;
    }
  }, {
    repetitions: validationsPerSession,
    on_timeline_start() {
      validationId += 1;
    },
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
        stampIds(data)
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
          stampIds(data)
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
