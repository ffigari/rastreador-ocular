const wgExt = jsPsych.extensions.webgazer;
import { instantiateMovementDetector } from './movement-detector/index.js';
import { instantiateCalibratorWith } from './calibrator.js';
import { instantiateEstimatorWith } from './estimator.js';

let movementDetectorIsReady = false;
document.addEventListener('rastoc_movement-detector:ready', () => {
  movementDetectorIsReady = true;
})

const movementDetector = instantiateMovementDetector();
const calibrator = instantiateCalibratorWith(wgExt, movementDetector);
const estimator = instantiateEstimatorWith(wgExt);

const state = {
  phase: 'idle',
  dataRecollection: {
    inProgress: false,
    intervalId: null,
    values: [],
  },
};
window.rastoc = {
  debugFaceAt(canvasElement) {
    movementDetector.debugFaceAt(canvasElement)
    return movementDetector;
  },
  calibrationIsNeeded() {
    return calibrator.calibrationIsNeeded();
  },
  checkDecalibration() {
    return calibrator.checkDecalibration();
  },
  get continueTo() {
    return {
      estimate() {
        if (state.phase !== 'estimating') {
          throw new Error(`No se puede continuar estimando por que la fase actual es '${state.phase}'`)
        }
        return estimator
      }
    }
  },
  get switchTo () {
    return {
      idle() {
        if (state.phase === 'idle') {
          throw new Error(
            `No se pudo cambiar a 'idle' porque la fase ya actual es 'idle'.`
          );
        }

        let estimatedGazes = null;
        if (state.dataRecollection.inProgress) {
          estimatedGazes = [...state.dataRecollection.values].map(({
            estimatedAt, estimation
          }) => ({
            name: 'gaze-estimation',
            ts: estimatedAt,
            x: estimation[0],
            y: estimation[1],
            quality: {
              // TODO: Armar algo para poder extrapolar alguna medida de
              //       confianza.
              //       Una primer opción es al momento de la estimación usar
              //       la distancia de los ojos al promedio de las posiciones
              //       de los momentos de calibración
              confidence: 1,
            }
          }));
          clearInterval(state.dataRecollection.intervalId);
          Object.assign(state.dataRecollection, {
            inProgress: false,
            intervalId: null,
            values: [],
          })
        }

        Object.assign(state, {
          phase: 'idle',
        })
        wgExt.pause();

        return estimatedGazes
      },
      async calibrating() {
        if (state.phase !== 'idle') {
          throw new Error(`No se pudo cambiar a 'calibrating' porque la fase actual no es 'idle'.`)
        }

        Object.assign(state, {
          phase: 'calibrating',
        })
        await wgExt.resume();
        await calibrator.reset()
        return calibrator
      },
      async estimating() {
        if (state.phase !== 'idle') {
          throw new Error("No se pudo cambiar a 'estimating' porque la fase actual no es 'idle'.");
        }

        if (state.dataRecollection.intervalId !== null) {
          throw new Error(
            "Al entrar en la fase de estimación no se debería estar recolectando data."
          );
        }

        Object.assign(state, {
          phase: 'estimating',
        })
        await wgExt.resume();

        Object.assign(state.dataRecollection, {
          inProgress: true,
          intervalId: setInterval(async () => {
            try {
              // Ideally this try catch should not be needed but there seems
              // to be a race condition in which this interval is not cleared
              // in time
              state.dataRecollection.values.push({
                estimatedAt: new Date,
                estimation: await estimator.currentPrediction()
              })
              if (!state.dataRecollection.inProgress) {
                clearInterval(state.dataRecollection.intervalId)
              }
            } catch (e) {
              console.warn(e)
            }
          }, 1000 / 24)
        })

        return estimator
      },
    }
  },
};
  
window.addEventListener('load', () => {
  if (movementDetectorIsReady) {
    document.dispatchEvent(new Event('rastoc:ready'));
  } else {
    document.addEventListener('rastoc_movement-detector:ready', () => {
      document.dispatchEvent(new Event('rastoc:ready'));
    })
  }
});
