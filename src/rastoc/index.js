// TODO: Review what gets reused and what gets deleted from here
//
// import { instantiateMovementDetector } from './movement-detector/index.js';
// import { instantiateCalibratorWith } from './calibrator.js';
// import { instantiateEstimator } from './estimator.js';
// import { instantiateVisualizerWith } from './visualizer.js';
// 
// const mainEventsNames = [
//   'rastoc:gaze-estimated',
//   'rastoc:calibration',
//   'rastoc:decalibration',
// ];
// 
// async () => {
//   if (!jsPsych.extensions.webgazer) {
//     throw new Error("The WebGazer extension from JSPsych is not loaded.");
//   }
// 
//   const movementDetector = {
//     debugFaceAt(canvas) { },
//     useNextFrameAsValidPosition() { },
//     distanceToValidPosition() { return 0; },
//     start: {
//       calibration() { },
//       detection() { },
//     },
//     stop() { },
//   };
//   const calibrator = instantiateCalibratorWith(movementDetector);
//   const estimator = instantiateEstimator(movementDetector);
//   const visualizer = instantiateVisualizerWith(estimator)
// 
//   const state = {
//     phase: null,
//   };
//   window.rastoc = {
//     visualizer,
//     movementDetector,
//     debugFaceAt(canvasElement) {
//       movementDetector.debugFaceAt(canvasElement)
//     },
//     calibrationIsNeeded() {
//       return calibrator.calibrationIsNeeded();
//     },
//     switchTo: {
//       async calibrating() {
//         if (state.phase === 'calibrating') {
//           throw new Error("Ya se está calibrando");
//         }
// 
//         if (state.phase === 'estimating') {
//           estimator.stop();
//         }
//         Object.assign(state, {
//           phase: 'calibrating',
//         })
//         await calibrator.reset()
//         return calibrator
//       },
//       async estimating() {
//         if (state.phase === 'estimating') {
//           throw new Error("Ya se está estimando");
//         }
// 
//         await estimator.resume();
//         Object.assign(state, {
//           phase: 'estimating',
//         })
// 
//         return { visualizer };
//       },
//     },
//     async start() {
//       await rastoc.switchTo.estimating();
//       state.events = [];
//       state.handler = ({ detail: gazeEvent }) => state.events.push(gazeEvent);
//       ;
//       mainEventsNames.forEach((eventName) => document.addEventListener(
//         eventName,
//         state.handler
//       ));
//     },
//     finish() {
//       movementDetector.stop();
//       mainEventsNames.forEach((
//         eventName
//       ) => document.removeEventListener(eventName, state.handler))
//       return state.events;
//     },
//   };
// 
//   document.addEventListener('rastoc_movement-detector:ready', () => {
//     document.dispatchEvent(new Event('rastoc:ready'));
//   })
// }

document.addEventListener('DOMContentLoaded', async () => {
  if (typeof webgazer === 'undefined' || !window.webgazer) {
    console.error(
      'WebGazer was not found. Make sure the js file has been loaded.'
    );
    document.dispatchEvent(new Event('rastoc:webgazer-not-found'));
    return;
  }
  document.dispatchEvent(new Event('rastoc:webgazer-found'));
});

const state = {
  // TODO: Replace this count with an array containing the calibration mappings
  calibrationPointsCount: 0,
  // TODO: Instead of storing this boolean, store last features
  eyeFeaturesJustWereAvailable: false,
  // TODO: Add object to store criteria relevant computed data
};

const _clickCalibrationHandler = ({ clientX: x, clientY: y }) => {
  // TODO: If eye features are not available return
  webgazer.recordScreenPosition(x, y, 'click');
  // TODO: Store new calibration data
  state.calibrationPointsCount++;
  // TODO: Recompute data needed for movement detection criteria
  //       This should be mean of each one of the received values (origin,
  //       width, height)
  document.dispatchEvent(new Event('rastoc:point-calibrated'));
};

// TODO: This could be placed in a separate file dedicated to webgazer wrapper
//       related stuff.
document.addEventListener('webgazer:eye-features-update', ({
  detail: lastEyeFeatures,
}) => {
  state.lastEyeFeatures = lastEyeFeatures;
  if (lastEyeFeatures) {
    let update = {};
    ['left', 'right'].forEach(side => {
      if (!lastEyeFeatures[side]) {
        update[side] = null;
        return;
      }
      const e = lastEyeFeatures[side];
      update[side] = {
        origin: { x: e.imagex, y: e.imagey },
        width: e.width,
        height: e.height,
      };
    });
    document.dispatchEvent(new CustomEvent('rastoc:eye-features-update', {
      detail: update,
    }))
  }

  if (lastEyeFeatures && !state.eyeFeaturesJustWereAvailable) {
    state.eyeFeaturesJustWereAvailable = true;
    document.dispatchEvent(new Event('rastoc:eye-features-went-available'));
  }
  if (!lastEyeFeatures && state.eyeFeaturesJustWereAvailable) {
    state.eyeFeaturesJustWereAvailable = false;
    document.dispatchEvent(new Event('rastoc:eye-features-went-unavailable'));
  }
});

const markAsDecalibrated = () => {
  // TODO: Update state (calibration must not be reset)
  // TODO: dispatch decalibration
}

const markAsPositionRecovered = () => {
  // TODO: Update state (calibration must not be reset)
  // TODO: dispatch position recovered
}

document.addEventListener('rastoc:eye-features-went-unavailable', () => {
  // TODO:
});

document.addEventListener('rastoc:calibration-finished', () => {
  // TODO:
});

document.addEventListener('rastoc:eye-features-update', ({
  detail: update,
}) => {
  // TODO: Verify whether criteria is met
  //   if system is not calibrated
  //     return
  //
  //   if last feature did not break criteria but this one does:
  //     markAsDecalibrated
  //
  //   if this feature breaks criteria but last feature met it:
  //     markAsPositionRecovered
});

window.rastoc = {
  startCalibrationPhase() {
    webgazer.clearData();
    // TODO: Clear calibration array

    // TODO: Stop movement detection
    // TODO: Clear movement decalibration computed data
    state.calibrationPointsCount = 0;
    webgazer.resume();

    webgazer.showPredictionPoints(false);
    const _enableGazeVisualizationAfterFirstClick = () => {
      webgazer.showPredictionPoints(true);
      document.removeEventListener('click', _enableGazeVisualizationAfterFirstClick);
    };
    setImmediate(() => {
      document.addEventListener('click', _clickCalibrationHandler);
      document.addEventListener('click', _enableGazeVisualizationAfterFirstClick);
      document.dispatchEvent(new Event('rastoc:calibration-started'));
    });
  },
  endCalibrationPhase() {
    document.removeEventListener('click', _clickCalibrationHandler);
    webgazer.showPredictionPoints(false);
    document.dispatchEvent(new Event('rastoc:calibration-finished'));
    // TODO: Enable movement detection back
  },
  get calibrationPointsCount() {
    return state.calibrationPointsCount;
  }
};
