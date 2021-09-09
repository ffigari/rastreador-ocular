jsPsych.plugins['infinite-validation'] = (function(){
  return {
    info: {
      name: 'infinite-validation',
    },
    trial: async function(display_element, trial) {
      const estimator = await rastoc.switchTo.estimating()

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
          <p>
            Se reportan los promedios de los errores sobre los nueve estímulos
            mostrados.
          </p>
          <table>
            <tr>
              <th> ronda </th>
              <th> promedio de los errores lineales (px) </th>
              <th> promedio de los errores cuadrados (px<sup>2</sup>) </th>
            </tr>
            ${collectedMetrics.map((metrics, index) => `<tr>
              <th> ${index} </th>
              <th> ${metrics.average.linearError().toFixed(2)} </th>
              <th> ${metrics.average.squareError().toFixed(2)} </th>
            </tr>`).join('')}
          </table>
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
      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
