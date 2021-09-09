jsPsych.plugins['calibrate-eye-tracker'] = (function(){
  return {
    info: {
      name: 'calibrate-eye-tracker',
    },
    trial: async function(display_element, trial) {
      const calibrator = await rastoc.switchTo.calibrating()

      await displayHTML(`
        <p>
          Vamos a calibrar el sistema. <br>
          Te vamos a mostrar una serie de estímulos. A medida que aparezcan
          tenés que mirarlos y presionar la barra de espacio para indicar que
          los estás mirando. <br>
          Para comenzar presioná cualquier tecla.
        </p>
      `).at(display_element).untilAnyKeyIsPressed()

      let stimulus = drawer.appendCalibrationStimulus()
      await calibrator.runExplicitCalibration(
        (xPercentage, yPercentage) => {
          drawer.moveToPercentages(stimulus, xPercentage, yPercentage)
          return drawer.getCenterInPixels(stimulus)
        }
      )
      drawer.erasePoint(stimulus)

      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
