import { canvasDrawer, Loop } from '../utils.js';

let estimator;
export const instantiateEstimatorWith = (gazeEstimator) => {
  if (!estimator) {
    const state = {
      visualization: {
        isOn: false,
        elementId: null,
        loopCallbackIntervalId: null,
      },
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
      showVisualization () {
        if (state.visualization.isOn) {
          throw new Error('La visualización de la estimación ya está activada.');
        }

        const visualizationElement = canvasDrawer.appendMarkerFor.gaze();
        const intervalId = setInterval(async () => {
          const p = this.lastPrediction;
          if (!p) {
            // TODO: En este caso habría que esconder el marker
            return;
          }
          const [x, y] = p;
          canvasDrawer.moveToPixels(
            visualizationElement,
            x,
            y
          );
        }, 100)

        Object.assign(state.visualization, {
          isOn: true,
          elementId: visualizationElement.id,
          loopCallbackIntervalId: intervalId,
        });
      },
      hideVisualization() {
        if (!state.visualization.isOn) {
          throw new Error('La visualización de la predicción no está activada.');
        }

        document
          .getElementById(state.visualization.elementId)
          .remove();
        clearInterval(state.visualization.loopCallbackIntervalId);

        Object.assign(state.visualization, {
          isOn: false,
          elementId: null,
          loopCallbackIntervalId: null,
        });
      },
    };
  }
  return estimator;
}
