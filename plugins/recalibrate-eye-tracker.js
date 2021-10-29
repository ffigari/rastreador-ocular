jsPsych.plugins['recalibrate-eye-tracker'] = (function(){
  return {
    info: {
      name: 'recalibrate-eye-tracker',
    },
    trial: async function(display_element, trial) {
      const calibrator = await rastoc.switchTo.calibrating()

      // TODO: Reset rastoc and movement detector
      await displayHTML(`
        <p>
          Vamos a calibrar el sistema. <br>
          Te vamos a mostrar una serie de estímulos. A medida que aparezcan
          tenés que mirarlos y presionar la barra de espacio para indicar que
          los estás mirando. <br>
          Para comenzar presioná cualquier tecla.
        </p>
      `).at(display_element).untilAnyKeyIsPressed()

      await calibrator.runExplicitCalibration(drawer)

      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
