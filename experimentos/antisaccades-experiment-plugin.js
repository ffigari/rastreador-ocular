const randomBoolean = () => Math.random() < 0.5;
const sleep = async (ms) => new Promise(res => setTimeout(res, ms));

const drawRandomSaccadeTask = async () => {
  const timeBeforeShowingTaskInMs = 230
  const isAntisaccadeTask = randomBoolean()
  const targetAppearsInRightSide = randomBoolean()

  const trialConfig = {
    isAntisaccadeTask,
    targetAppearsInRightSide,
  };

  await sleep(1000);
  trialConfig.relevantDataStartsAt = new Date;

  const fixationMarker = canvasDrawer.appendMarkerFor.centerFixation();
  canvasDrawer.moveToPercentages(fixationMarker, 50, 50);

  await sleep(2000);
  canvasDrawer.erasePoint(fixationMarker);

  await sleep(timeBeforeShowingTaskInMs);

  const typeSignalMarker = isAntisaccadeTask
    ? canvasDrawer.appendMarkerFor.antisaccade.antiSignal()
    : canvasDrawer.appendMarkerFor.antisaccade.proSignal();
  canvasDrawer.moveToPercentages(typeSignalMarker, 50, 50);

  const targetMarker = canvasDrawer.appendMarkerFor.antisaccade.target();
  canvasDrawer.moveToPercentages(
    targetMarker,
    targetAppearsInRightSide ? 80 : 20,
    50
  );

  await sleep(2000);
  canvasDrawer.erasePoint(typeSignalMarker);
  canvasDrawer.erasePoint(targetMarker);

  trialConfig.relevantDataFinishesAt = new Date;
  await sleep(1000);

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
