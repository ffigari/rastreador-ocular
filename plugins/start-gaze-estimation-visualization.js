jsPsych.plugins['start-gaze-estimation-visualization'] = (function(){
  return {
    info: {
      name: 'start-gaze-estimation-visualization',
      parameters: {},
    },
    trial: async function(display_element, trial){
      const estimator = await rastoc.switchTo.estimating()

      estimator.showVisualization();
      jsPsych.finishTrial();
    },
  };
})();
