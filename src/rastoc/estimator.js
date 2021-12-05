import { canvasDrawer, Loop } from '../utils.js';

let estimator;
export const instantiateEstimatorWith = (gazeEstimator) => {
  if (!estimator) {
    const state = {
      lastPrediction: null,
    }

    const predictionUpdaterLoop = new Loop(async () => {
      const prediction = await gazeEstimator.getCurrentPrediction();
      if (prediction === null) {
        state.lastPrediction = null;
      } else {
        state.lastPrediction = [prediction.x, prediction.y];
      }
    })

    estimator = {
      start() {
        predictionUpdaterLoop.turn.on();
      },
      stop() {
        predictionUpdaterLoop.turn.off();
      },
      get lastPrediction() {
        return state.lastPrediction;
      },
    };
  }
  return estimator;
}
