jsPsych.plugins['finish-eye-tracking'] = (function(){
  return {
    info: {
      name: 'finish-eye-tracking',
      parameters: {},
    },
    trial: function(display_element, trial){
      const estimator = eyeTracking.continueTo.estimate()

      estimator.hideVisualization();
      jsPsych.data.get().localSave('json','webgazer-sample-data.json');
      jsPsych.finishTrial();

      eyeTracking.switchTo.idle()
    },
  }
})();
