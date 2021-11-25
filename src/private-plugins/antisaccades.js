const randomBoolean = () => Math.random() < 0.5

const drawRandomSaccadeTask = async () => {
  const timeBeforeShowingTaskInMs = 230
  const isAntisaccadeTask = randomBoolean()
  const targetAppearsInRightSide = randomBoolean()

  const trialConfig = {
    isAntisaccadeTask,
    targetAppearsInRightSide,
    // TODO: Ver de agregar alguna lista de eventos con un formato estandarizado
    //       Si se les define algo como "eventos con coordenadas y alguna
    //       descripcion" entonces podría usarse en os gráficos que se produzcan
    //       independientemente del experimento
  };

  const fixationMarker = drawer.appendMarkerFor.centerFixation();
  drawer.moveToPercentages(fixationMarker, 50, 50);

  await sleep(2000);
  drawer.erasePoint(fixationMarker);

  await sleep(timeBeforeShowingTaskInMs);

  const typeSignalMarker = isAntisaccadeTask
    ? drawer.appendMarkerFor.antisaccade.antiSignal()
    : drawer.appendMarkerFor.antisaccade.proSignal();
  drawer.moveToPercentages(typeSignalMarker, 50, 50);

  const targetMarker = drawer.appendMarkerFor.antisaccade.target();
  drawer.moveToPercentages(
    targetMarker,
    targetAppearsInRightSide ? 80 : 20,
    50
  );

  await sleep(2000);
  drawer.erasePoint(typeSignalMarker);
  drawer.erasePoint(targetMarker);

  return trialConfig;
}

jsPsych.plugins['antisaccades'] = (function(){
  return {
    info: {
      name: 'antisaccades',
    },
    trial: async function(display_element, trial) {
      const trialConfig = await drawRandomSaccadeTask();

      jsPsych.finishTrial({
        trial: {
          config: trialConfig,
        }
      })
    },
  }
})();
