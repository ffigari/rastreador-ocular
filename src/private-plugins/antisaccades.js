const drawRandomSaccadeTask = async () => {
  const randomBoolean = () => Math.random() < 0.5

  const timeBeforeShowingTaskInMs = 230
  const isAntisaccadeTask = randomBoolean()
  const targetAppearsInRightSide = randomBoolean()
  const data = {
    name: 'antisaccade-task',
    startedAt: new Date,
    endedAt: null,
    config: { isAntisaccadeTask, targetAppearsInRightSide },
    timestamps: {
      fixation: {
        appeareance: null,
        erasure: null,
        coordinates: null,
      },
      typeSignal: {
        appeareance: null,
        erasure: null,
        coordinates: null,
      },
      target: {
        appeareance: null,
        erasure: null,
        coordinates: null,
      },
    },
  }

  const fixationMarker = drawer.appendMarkerFor.centerFixation()
  drawer.moveToPercentages(fixationMarker, 50, 50)
  Object.assign(data.timestamps.fixation, {
    coordinates: drawer.getCenterInPixels(fixationMarker),
    appeareance: new Date,
  })

  await sleep(2000)
  drawer.erasePoint(fixationMarker)
  data.timestamps.fixation.erasure = new Date

  await sleep(timeBeforeShowingTaskInMs)

  const typeSignalMarker = isAntisaccadeTask
    ? drawer.appendMarkerFor.antisaccade.antiSignal()
    : drawer.appendMarkerFor.antisaccade.proSignal()
  drawer.moveToPercentages(typeSignalMarker, 50, 50)
  Object.assign(data.timestamps.typeSignal, {
    coordinates: drawer.getCenterInPixels(typeSignalMarker),
    appeareance: new Date,
  })

  const targetMarker = drawer.appendMarkerFor.antisaccade.target()
  drawer.moveToPercentages(
    targetMarker,
    targetAppearsInRightSide ? 80 : 20,
    50
  )
  Object.assign(data.timestamps.target, {
    coordinates: drawer.getCenterInPixels(targetMarker),
    appeareance: new Date,
  })

  await sleep(2000)
  drawer.erasePoint(typeSignalMarker)
  data.timestamps.typeSignal.erasure = new Date
  drawer.erasePoint(targetMarker)
  data.timestamps.target.erasure = new Date

  return Object.assign(data, { endedAt: new Date })
}

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

      const data = {
        name: 'antisaccade-experiment',
        startedAt: new Date,
        endedAt: null,
        runs: [],
      }
      for (let i = 0; i < runsCount; ++i) {
        data.runs.push(await drawRandomSaccadeTask())
      }

      // TODO: Pass this data to jspsych
      Object.assign(data, { endedAt: new Date })
      estimator.hideVisualization()
      rastoc.switchTo.idle()
      jsPsych.finishTrial();
    },
  }
})();
