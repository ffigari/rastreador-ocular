import { canvasDrawer, Loop } from '../utils.js';

const wgExt = jsPsych.extensions.webgazer;
let estimator;
export const instantiateEstimator = () => {
  if (!estimator) {
    let cancelGazeUpdateHandler;
    estimator = {
      async resume() {
        await wgExt.resume();
        cancelGazeUpdateHandler = wgExt.onGazeUpdate((prediction) => {
          document.dispatchEvent(new CustomEvent('rastoc:gaze-estimated', {
            detail: {
              name: 'gaze-estimation',
              ts: new Date,
              x: prediction.x,
              y: prediction.y,
              quality: {
                // TODO: Armar algo para poder extrapolar alguna medida de
                //       confianza.
                //       Una primer opción es al momento de la estimación usar
                //       la distancia de los ojos al promedio de las posiciones
                //       de los momentos de calibración
                confidence: 1,
              }
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
