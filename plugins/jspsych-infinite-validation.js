jsPsych.plugins['infinite-validation'] = (function(){
  return {
    info: {
      name: 'infinite-validation',
    },
    trial: async function(display_element, trial) {
      const estimator = await eyeTracking.switchTo.estimating()

      estimator.showVisualization()

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

        const spaceWasPressed = await displayHTML(`
          <div>
            Resultados obtenidos hasta ahora:
            <ul>
              ${collectedMetrics.map((metrics) => {
                return `<li>${metrics.average.linearError()}</li>`
              }).join('')}
            </ul>
          </div>
          <p>
            Para realizar otra ronda de validación presioná la barra de espacio.
            <br>
            Para terminar presioná cualquier otro botón.
          </p>
        `).at(display_element).untilAnyKeyIsPressed()

        if (spaceWasPressed) continue
        else break
      }

      estimator.hideVisualization()
      eyeTracking.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
