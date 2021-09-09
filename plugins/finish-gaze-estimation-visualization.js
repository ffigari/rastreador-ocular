jsPsych.plugins['finish-gaze-estimation-visualization'] = (function(){
  return {
    info: {
      name: 'finish-gaze-estimation-visualization',
      parameters: {},
    },
    trial: function(display_element, trial){
      const estimator = rastoc.continueTo.estimate()

      estimator.hideVisualization();

      jsPsych.finishTrial();
      rastoc.switchTo.idle()
    },
  }
})();
