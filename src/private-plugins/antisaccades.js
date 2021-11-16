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
      const taskData = await drawRandomSaccadeTask();

      jsPsych.finishTrial({ taskData })
    },
  }
})();
