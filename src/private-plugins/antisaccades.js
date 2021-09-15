jsPsych.plugins['antisaccades'] = (function(){
  return {
    info: {
      name: 'antisaccades',
    },
    trial: async function(display_element, trial) {
      const estimator = await rastoc.switchTo.estimating()

      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
