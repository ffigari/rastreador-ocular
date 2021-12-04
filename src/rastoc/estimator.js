import { canvasDrawer } from '../utils.js';

let estimator;
export const instantiateEstimatorWith = (gazeEstimator) => {
  if (!estimator) {
    const state = {
      visualization: {
        isOn: false,
        elementId: null,
        loopCallbackIntervalId: null,
      }
    }
    estimator = {
      async currentPrediction() {
        const current = await gazeEstimator.getCurrentPrediction();
        if (current === null) {
          throw new Error(`WebGazer retornó 'null' para la predicción actual.`);
        }
        return [current.x, current.y];
      },
      showVisualization () {
        if (state.visualization.isOn) {
          throw new Error('La visualización de la estimación ya está activada.');
        }

        const visualizationElement = canvasDrawer.appendMarkerFor.gaze();
        const intervalId = setInterval(async () => {
          try {
            // Ideally this try catch should not be needed but there seems to be
            // a race condition in which this interval is not cleared in time
            const [x, y] = await this.currentPrediction();
            canvasDrawer.moveToPixels(
              visualizationElement,
              x,
              y
            );
          } catch (e) {
            console.warn(e)
          }
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
