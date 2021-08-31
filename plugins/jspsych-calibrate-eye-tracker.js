jsPsych.plugins['calibrate-eye-tracker'] = (function(){
  return {
    info: {
      name: 'calibrate-eye-tracker',
    },
    trial: async function(display_element, trial) {
      const calibrator = await eyeTracking.switchTo.calibrating()

      const stimulus = drawer.appendCalibrationStimulus()
      await calibrator.runExplicitCalibration(
        (xPercentage, yPercentage) => {
          drawer.moveToPercentages(stimulus, xPercentage, yPercentage)
        },
        async (extendCalibrationWith) => {
          await new Promise((resolve) => {
            stimulus.addEventListener('click', (e) => {
              extendCalibrationWith(e.clientX, e.clientY)
              resolve()
            }, { once: true, })
          })
        },
      )
      drawer.erasePoint(stimulus)

      eyeTracking.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
