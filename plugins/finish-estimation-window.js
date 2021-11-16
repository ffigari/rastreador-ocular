jsPsych.plugins['finish-estimation-window'] = (function(){
  return {
    info: {
      name: 'finish-estimation-window',
      parameters: {},
    },
    trial: async function(display_element, trial) {
      estimator.hideVisualization()
      const estimationWindowData = rastoc.switchTo.idle();
      jsPsych.finishTrial({ estimationWindowData })
    },
  }
})();
