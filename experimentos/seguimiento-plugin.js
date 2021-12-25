const sleep = async (ms) => new Promise(res => setTimeout(res, ms));
// https://stackoverflow.com/a/6274381/2923526
const shuffle = (a) => {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Interpolates between two points of format [x, y]
// Assumes `source = f(0)` and `target = f(1)`
// Returns `f(proportion)`
const interpolate2D = (source, target, proportion) => {
  const x = source[0] + (target[0] - source[0]) * proportion;
  const y = source[1] + (target[1] - source[1]) * proportion;
  return [x, y];
}

const pointsToVisit = [
  [20, 20], [20, 50], [20, 80],
  [50, 20], [50, 50], [50, 80],
  [80, 20], [80, 50], [20, 80],
];
const msBetweenTargets = 2000;

const drawRandomSeguimientoTask = async () => {
  const shuffledPointsToVisit = shuffle(pointsToVisit);
  const trialConfig = {
    stimulusPositions: [],
  };

  await sleep(500);
  const fixationMarker = canvasDrawer.appendMarkerFor.centerFixation();
  canvasDrawer.moveToPercentages(
    fixationMarker,
    shuffledPointsToVisit[0][0],
    shuffledPointsToVisit[0][1]
  );
  await sleep(500);
  canvasDrawer.erasePoint(fixationMarker);
  trialConfig.relevantDataStartsAt = new Date;

  const followUpMarker = canvasDrawer.appendMarkerFor.followUp();
  canvasDrawer.hidePoint(followUpMarker);
  for (let i = 0; i < shuffledPointsToVisit.length; ++i) {
    const source = shuffledPointsToVisit[i];
    const target = shuffledPointsToVisit[(i + 1) % shuffledPointsToVisit.length];

    await new Promise((res) => {
      let movementStartTs;
      const drawer = (ts) => {
        if (!movementStartTs) {
          movementStartTs = ts;
        }
        const elapsed = ts - movementStartTs;
        if (elapsed > msBetweenTargets) {
          return res();
        }
        const position = interpolate2D(source, target, elapsed / msBetweenTargets);
        canvasDrawer.moveToPercentages(followUpMarker, position[0], position[1]);
        canvasDrawer.showPoint(followUpMarker);

        const positionInPixels = canvasDrawer.getCenterInPixels(followUpMarker);
        trialConfig.stimulusPositions.push({
          name: 'follow-up-stimulus-position',
          ts: new Date,
          x: positionInPixels[0],
          y: positionInPixels[1],
        })

        window.requestAnimationFrame(drawer);
      }
      window.requestAnimationFrame(drawer);
    })
  }
  canvasDrawer.erasePoint(followUpMarker);
  trialConfig.relevantDataFinishesAt = new Date;
  await sleep(500);
  return trialConfig;
}

jsPsych.plugins['seguimiento'] = (function(){
  return {
    info: {
      name: 'seguimiento',
    },
    trial: async function(display_element, trial) {
      const trialConfig = await drawRandomSeguimientoTask();

      jsPsych.finishTrial({
        trial: {
          config: trialConfig,
        }
      })
    },
  }
})();
