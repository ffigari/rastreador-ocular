import { canvasDrawer, Loop } from '../utils.js';

let estimator;
export const instantiateEstimator = (movementDetector) => {
  const wgExt = jsPsych.extensions.webgazer;
  if (!estimator) {
    let cancelGazeUpdateHandler;
    estimator = {
      async resume() {
        await wgExt.resume();
        cancelGazeUpdateHandler = wgExt.onGazeUpdate((prediction) => {
          document.dispatchEvent(new CustomEvent('rastoc:gaze-estimated', {
            // La medida de confianza es una exponencial inversa en función de
            // la distancia promedio de los ojos a las posiciones válidas.
            // f(0)  = 1
            // f(5)  = 0.368
            // f(10) = 0.135
            const confidence = Math.pow(
              Math.E,
              - movementDetector.distanceToValidPosition() / 5
            );
            detail: {
              name: 'gaze-estimation',
              ts: new Date,
              x: prediction.x,
              y: prediction.y,
              confidence,
            },
          }))
        })
      },
      stop() {
        cancelGazeUpdateHandler();
        wgExt.pause();
      },
    };
  }
  return estimator;
}
