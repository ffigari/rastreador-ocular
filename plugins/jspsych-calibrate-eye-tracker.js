jsPsych.plugins['calibrate-eye-tracker'] = (function(){
  return {
    info: {
      name: 'calibrate-eye-tracker',
    },
    trial: async function(display_element, trial) {
      const calibrator = await eyeTracking.switchTo.calibrating()

      let stimulus = drawer.appendCalibrationStimulus()
      await calibrator.runExplicitCalibration(
        (xPercentage, yPercentage) => {
          drawer.moveToPercentages(stimulus, xPercentage, yPercentage)
          return drawer.getCenterInPixels(stimulus)
        }
      )
      drawer.erasePoint(stimulus)

      eyeTracking.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
