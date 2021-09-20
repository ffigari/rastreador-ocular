jsPsych.plugins['antisaccades'] = (function(){
  return {
    info: {
      name: 'antisaccades',
    },
    trial: async function(display_element, trial) {
      const estimator = await rastoc.switchTo.estimating()
      estimator.showVisualization()

      const runsCount = 5
      await displayHTML(`
        <h2>Instrucciones</h2>
        <p>
          Vamos a realizar un experimento de antisacadas. <br>
          Se te mostrarán ${runsCount} iteraciones de tareas en las cuales un
          primer estímulo te indicará en qué dirección mirar respecto de un
          segundo estímulo. Si el primer estímulo es <span style="color: red;
          font-weight: bold;">rojo</span> tenés que mirar en la <span
          style="color: red; font-weight: bold;">dirección opuesta</span>. Si
          en cambio es <span style="color: green; font-weight:
          bold;">verde</span> tenés que mirar en la <span style="color: green;
          font-weight: bold;">misma dirección</span>. <br>
          Presioná cualquier tecla para comenzar.
       <p>
      `).at(display_element).untilAnyKeyIsPressed()

      // TODO: Add data recollection
      const drawRandomSaccadeTask = async () => {
        const randomBoolean = () => Math.random() < 0.5

        const timeBeforeShowingTaskInMs = 230
        const isAntisaccadeTask = randomBoolean()
        const targetAppearsInRightSide = randomBoolean()

        const fixationMarker = drawer.appendMarkerFor.centerFixation()
        drawer.moveToPercentages(fixationMarker, 50, 50)

        await sleep(2000)
        drawer.erasePoint(fixationMarker)

        await sleep(timeBeforeShowingTaskInMs)

        const typeSignalMarker = isAntisaccadeTask
          ? drawer.appendMarkerFor.antisaccade.antiSignal()
          : drawer.appendMarkerFor.antisaccade.proSignal()
        drawer.moveToPercentages(typeSignalMarker, 50, 50)

        const targetMarker = drawer.appendMarkerFor.antisaccade.target()
        drawer.moveToPercentages(
          targetMarker,
          targetAppearsInRightSide ? 80 : 20,
          50
        )

        await sleep(2000)
        drawer.erasePoint(typeSignalMarker)
        drawer.erasePoint(targetMarker)
      }

      for (let i = 0; i < runsCount; ++i) {
        await drawRandomSaccadeTask()
      }

      estimator.hideVisualization()
      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
