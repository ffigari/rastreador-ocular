jsPsych.plugins['validate-last-calibration'] = (function(){
  return {
    info: {
      name: 'validate-last-calibration',
    },
    trial: async function(display_element, trial) {
      const estimator = await rastoc.switchTo.estimating()

      await displayHTML(`
        <p>
          Ahora vamos a correr una ronda de validación para ver cómo salió la
          calibración. <br>
          Al igual que con la calibración, tenés que presionar la barra de
          espacio a medida que aparecen estímulos y los mirás. <br>
          Presioná cualquier tecla para continuar.
        </p>
      `).at(display_element).untilAnyKeyIsPressed()

      estimator.showVisualization()

      const metrics = await estimator.runValidationRound(drawer)

      await displayHTML(`
        <table>
          <tr>
            <th> coordenadas del estímulo (en porcentajes) </th>
            <th> error cuadrádo (en píxeles cuadrados) </th>
            <th> error lineal (en píxeles) </th>
          </tr>
          ${metrics.rawResults.map(({
            groundTruthPercentages: [x, y], squareError, linearError
          }) => `<tr>
            <td> (${x}, ${y}) </td>
            <td> ${squareError.toFixed(2)} </td>
            <td> ${linearError.toFixed(2)} </td>
          </tr>`).join('')}
        </table>
        <p>
          Presioná cualquier tecla para terminar
        </p>
      `).at(display_element).untilAnyKeyIsPressed()

      estimator.hideVisualization()
      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
