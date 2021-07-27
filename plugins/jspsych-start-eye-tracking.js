jsPsych.plugins['start-eye-tracking'] = (function(){
  return {
    info: {
      name: 'start-eye-tracking',
      parameters: {},
    },
    trial: function(display_element, trial){
      eyeTracking.startPredictionVisualization();
      jsPsych.finishTrial();
    },
  };
})();
