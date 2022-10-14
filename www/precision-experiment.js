const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('csv', 'precision-experiment.csv');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

let validationStimulusCoordinates;
let idx;
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
