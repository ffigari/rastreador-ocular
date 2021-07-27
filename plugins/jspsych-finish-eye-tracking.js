jsPsych.plugins['finish-eye-tracking'] = (function(){
  return {
    info: {
      name: 'finish-eye-tracking',
      parameters: {},
    },
    trial: function(display_element, trial){
      eyeTracking.stopPredictionVisualization();
      jsPsych.data.get().localSave('json','webgazer-sample-data.json');
      jsPsych.finishTrial();
    },
  }
})();
