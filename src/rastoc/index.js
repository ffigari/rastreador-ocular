import './movement-detection.js'
import { instantiateCalibratorWith } from './calibrator.js'
import { instantiateEstimatorWith } from './estimator.js'
const wgExt = jsPsych.extensions.webgazer

let movementDetectorIsReady = false;
document.addEventListener('rastoc_movement-detector:ready', () => {
  movementDetectorIsReady = true;
})

const state = {
  phase: 'idle',
  dataRecollection: {
    inProgress: false,
    intervalId: null,
    values: [],
  },
  atLeastOneCalibrationWasDone: false,
  decalibrationEvents: []
}

// TODO: This should listen to an event from the 'calibrator'. That module has
//       to listen to the events from the movement detector. No readyness check
//       is needed since no interaction will be done with any of the modules
//       until rastoc does not send the ready signal
document.addEventListener('movement-detector:movement:detected', () => {
  if (state.decalibrationEvents.length > 0) {
    // Movement was already reported
    // It would make more sense for the calibrator to listen to this movement
    // related continous events and fire one single event when it decides that
    // the system got decalibrated
    return;
  }
  state.decalibrationEvents = [
    { name: 'decalibration-detected', ts: new Date }
  ];
});
document.addEventListener('calibrator:system-calibrated', () => {
  state.atLeastOneCalibrationWasDone = true;
  state.decalibrationEvents = [];
})

const calibrator = instantiateCalibratorWith(wgExt, movementDetector);
const estimator = instantiateEstimatorWith(wgExt);
// TODO: Add a method to indicate the face debugging canvas
window.rastoc = {
  calibrationIsNeeded() {
    if (!state.atLeastOneCalibrationWasDone) {
      return true;
    }
    const {
      decalibrationWasDetectedSinceLastCalibration
    } = this.checkDecalibration();
    return decalibrationWasDetectedSinceLastCalibration;
  },
  checkDecalibration() {
    return {
      decalibrationWasDetectedSinceLastCalibration: state.decalibrationEvents.length > 0,
      decalibrationEvents: state.decalibrationEvents,
    };
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

        if (state.atLeastOneCalibrationWasDone) {
          await calibrator.reset()
        }

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
