jsPsych.plugins['start-eye-tracking'] = (function(){
  return {
    info: {
      name: 'start-eye-tracking',
      parameters: {},
    },
    trial: async function(display_element, trial){
      const estimator = await eyeTracking.switchTo.estimating()

      estimator.showVisualization();
      jsPsych.finishTrial();
    },
  };
})();
