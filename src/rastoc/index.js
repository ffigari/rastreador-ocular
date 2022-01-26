import { instantiateMovementDetector } from './movement-detector/index.js';
import { instantiateCalibratorWith } from './calibrator.js';
import { instantiateEstimator } from './estimator.js';
import { instantiateVisualizerWith } from './visualizer.js';

const mainEventsNames = [
  'rastoc:gaze-estimated',
  'rastoc:calibration',
  'rastoc:decalibration',
];

async () => {
  if (!jsPsych.extensions.webgazer) {
    throw new Error("The WebGazer extension from JSPsych is not loaded.");
  }

  const movementDetector = {
    debugFaceAt(canvas) { },
    useNextFrameAsValidPosition() { },
    distanceToValidPosition() { return 0; },
    start: {
      calibration() { },
      detection() { },
    },
    stop() { },
  };
  const calibrator = instantiateCalibratorWith(movementDetector);
  const estimator = instantiateEstimator(movementDetector);
  const visualizer = instantiateVisualizerWith(estimator)

  const state = {
    phase: null,
  };
  window.rastoc = {
    visualizer,
    movementDetector,
    debugFaceAt(canvasElement) {
      movementDetector.debugFaceAt(canvasElement)
    },
    calibrationIsNeeded() {
      return calibrator.calibrationIsNeeded();
    },
    switchTo: {
      async calibrating() {
        if (state.phase === 'calibrating') {
          throw new Error("Ya se está calibrando");
        }

        if (state.phase === 'estimating') {
          estimator.stop();
        }
        Object.assign(state, {
          phase: 'calibrating',
        })
        await calibrator.reset()
        return calibrator
      },
      async estimating() {
        if (state.phase === 'estimating') {
          throw new Error("Ya se está estimando");
        }

        await estimator.resume();
        Object.assign(state, {
          phase: 'estimating',
        })

        return { visualizer };
      },
    },
    async start() {
      await rastoc.switchTo.estimating();
      state.events = [];
      state.handler = ({ detail: gazeEvent }) => state.events.push(gazeEvent);
      ;
      mainEventsNames.forEach((eventName) => document.addEventListener(
        eventName,
        state.handler
      ));
    },
    finish() {
      movementDetector.stop();
      mainEventsNames.forEach((
        eventName
      ) => document.removeEventListener(eventName, state.handler))
      return state.events;
    },
  };

  document.addEventListener('rastoc_movement-detector:ready', () => {
    document.dispatchEvent(new Event('rastoc:ready'));
  })
}

// TODO: Replicate JSPsych's initialization of WG
// TODO: Figure out how to reuse WG's stuff for the video and the canvas
// TODO: Subscribe to WG's eye patches update and draw them over the debugging
//       canvas that has the video
// TODO: Reimplement movement detection by reusing WG eye patches
window.rastoc = {
  resetCalibration() {
    // TODO: Reset movement detection data
    webgazer.clearData();
  },
  mapCoordinateToGaze(x, y) {
    // TODO: Add gaze position as valid position
    webgazer.recordScreenPosition(x, y, 'click');
  },
};
