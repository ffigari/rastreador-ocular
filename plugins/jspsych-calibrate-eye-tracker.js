jsPsych.plugins['calibrate-eye-tracker'] = (function(){
  return {
    info: {
      name: 'calibrate-eye-tracker',
    },
    trial: async function(display_element, trial) {
      const calibrator = await eyeTracking.switchTo.calibrating()

      const stimulus = drawer.appendCalibrationStimulus()
      for (const [xPercentage, yPercentage] of [
        [10,10], [10,50], [10,90],
        [50,10], [50,50], [50,90],
        [90,10], [90,50], [90,90],
      ]) {
        drawer.moveToPercentages(stimulus, xPercentage, yPercentage)
        await new Promise((resolve) => {
          stimulus.addEventListener('click', (e) => {
            calibrator.extendCalibrationWith(e)
            resolve()
          }, { once: true, })
        })
      }
      drawer.erasePoint(stimulus)

      eyeTracking.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
