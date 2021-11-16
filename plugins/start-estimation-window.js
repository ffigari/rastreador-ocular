jsPsych.plugins['start-estimation-window'] = (function(){
  return {
    info: {
      name: 'start-estimation-window',
      parameters: {},
    },
    trial: async function(display_element, trial) {
      const estimator = await rastoc.switchTo.estimating()
      estimator.showVisualization()
      jsPsych.finishTrial()
    },
  }
})();
