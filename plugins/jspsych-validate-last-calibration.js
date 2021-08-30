jsPsych.plugins['validate-last-calibration'] = (function(){
  return {
    info: {
      name: 'validate-last-calibration',
    },
    trial: async function(display_element, trial) {
      const estimator = await eyeTracking.switchTo.estimating()

      // TODO: Enable estimation visualization
      // TODO: Validate a calibration was previously done
      // TODO: Retrieve the coordinates of points shown to the user
      // TODO: Show the same points in a randomized order
      // TODO: Para cada punto medir los errores cuadrados al centro del punto

      eyeTracking.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
