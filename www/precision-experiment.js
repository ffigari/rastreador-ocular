const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('csv', 'precision-experiment.csv');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

let validationStimulisCoordinates;
jsPsych.run([{
  type: jsPsychWebgazerInitCamera,
}, {
  type: rastocJSPsych.EventsTrackingStart,
}, {
  type: jsPsychVirtualChinrest,
}, {
  repetitions: 2, //10,
  timeline: [rastocJSPsych.calibrate.assistedly("fullscreen"), {
    repetitions: 2, //10,
    timeline: [{
      type: jsPsychPsychophysics,
      stimuli: [{
          obj_type: 'cross',
          origin_center: true,
          startX: 0,
          startY: 0,
          show_start_time: 100,
          show_end_time: 900,
          line_length: 40,
      }],
      response_ends_trial: false,
      trial_duration: 1000,
      extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
      on_finish(data) {
        data["trial-tag"] = "fixation-marker";
        data["start-x"] = 0;
        data["start-y"] = 0;
        validationStimulisCoordinates = 
          rastocJSPsych.getCalibrationStimulusCoordinates();
      },
    }],
  }],
}])
