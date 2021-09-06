jsPsych.plugins['calibrate-eye-tracker'] = (function(){
  return {
    info: {
      name: 'calibrate-eye-tracker',
    },
    trial: async function(display_element, trial) {
      const calibrator = await eyeTracking.switchTo.calibrating()

      display_element.innerHTML = `
      <p>
        Vamos a calibrar el sistema. <br>
        Te vamos a mostrar una serie de estímulos. A medida que aparezcan tenés
        que mirarlos y presionar la barra de espacio para indicar que los estás
        mirando. <br>
        Para comenzar presioná cualquier tecla.
      </p>
      `
      await forAnyKeyOn(document)
      display_element.innerHTML = ``

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
