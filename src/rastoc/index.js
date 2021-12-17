import { instantiateMovementDetector } from './movement-detector/index.js';
import { instantiateCalibratorWith } from './calibrator.js';
import { instantiateEstimator } from './estimator.js';
import { instantiateVisualizerWith } from './visualizer.js';

const movementDetector = instantiateMovementDetector();
const calibrator = instantiateCalibratorWith(movementDetector);
const estimator = instantiateEstimator();
const visualizer = instantiateVisualizerWith(estimator)

const state = {
  phase: 'idle',
};
window.rastoc = {
  debugFaceAt(canvasElement) {
    movementDetector.debugFaceAt(canvasElement)
    return movementDetector;
  },
  calibrationIsNeeded() {
    return calibrator.calibrationIsNeeded();
  },
  get continueTo() {
    return {
      estimate() {
        if (state.phase !== 'estimating') {
          throw new Error(`No se puede continuar estimando por que la fase actual es '${state.phase}'`)
        }
        return { visualizer };
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

        if (state.phase === 'estimating') {
          estimator.stop();
        }

        Object.assign(state, {
          phase: 'idle',
        });
      },
      async calibrating() {
        if (state.phase !== 'idle') {
          throw new Error(`No se pudo cambiar a 'calibrating' porque la fase actual no es 'idle'.`)
        }

        Object.assign(state, {
          phase: 'calibrating',
        })
        await calibrator.reset()
        return calibrator
      },
      async estimating() {
        if (state.phase !== 'idle') {
          throw new Error("No se pudo cambiar a 'estimating' porque la fase actual no es 'idle'.");
        }

        await estimator.resume();
        Object.assign(state, {
          phase: 'estimating',
        })

        return { visualizer };
      },
    }
  },
  finish() {
    movementDetector.stop();
  },
};
  
document.addEventListener('rastoc_movement-detector:ready', () => {
  document.dispatchEvent(new Event('rastoc:ready'));
})
