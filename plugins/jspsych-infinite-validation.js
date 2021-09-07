jsPsych.plugins['infinite-validation'] = (function(){
  return {
    info: {
      name: 'infinite-validation',
    },
    trial: async function(display_element, trial) {
      const estimator = await eyeTracking.switchTo.estimating()

      await displayHTML(`
        <p>
          Vamos a realizar continuamente rondas de validación. Luego de cada una
          te reportaremos los resultados y podrás elegir si continuar con nuevas
          rondas de validación.
        <p>
      `).at(display_element).untilAnyKeyIsPressed()

      const collectedMetrics = []
      while (true) {
        collectedMetrics.push(await estimator.runValidationRound(drawer))

        // TODO: Display message
        // TODO: Show plot
        const spaceWasPressed = await displayHTML(`
          <ul>
            ${collectedMetrics.map((metrics) => {
              return `<li>${metrics.average.linearError()}</li>`
            })}
          </ul>
        `).at(display_element).untilAnyKeyIsPressed()

        if (spaceWasPressed) {
          break
        }
      }

      eyeTracking.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
