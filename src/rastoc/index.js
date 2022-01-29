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
  // list of features corresponding to the ones from last frame each time a
  // calibration point was added
  calibrationEyeFeatures: [],
  // eye features from last frame
  lastFrameEyeFeatures: null,
  calibrating: false,
  // TODO: Add object to store criteria relevant computed data
};

const _clickCalibrationHandler = ({ clientX: x, clientY: y }) => {
  if (!state.lastFrameEyeFeatures) {
    console.log('Calibration was not performed due to missing eye features.');
    return;
  }
  webgazer.recordScreenPosition(x, y, 'click');
  state.calibrationEyeFeatures.push(state.lastFrameEyeFeatures);
  document.dispatchEvent(new Event('rastoc:point-calibrated'));
};

// TODO: This could be placed in a separate file dedicated to webgazer wrapper
//       related stuff.
document.addEventListener('webgazer:eye-features-update', ({
  detail: eyeFeatures,
}) => {
  const eyeFeatureJustWereAvailable = !!state.lastFrameEyeFeatures;
  state.lastFrameEyeFeatures = null;
  if (eyeFeatures) {
    let update = {};
    ['left', 'right'].forEach(side => {
      if (!eyeFeatures[side]) {
        update[side] = null;
        return;
      }
      const e = eyeFeatures[side];
      update[side] = {
        origin: { x: e.imagex, y: e.imagey },
        width: e.width,
        height: e.height,
      };
    });
    state.lastFrameEyeFeatures = eyeFeatures;
    document.dispatchEvent(new CustomEvent('rastoc:eye-features-update', {
      detail: update,
    }))
  }

  if (eyeFeatures && !eyeFeatureJustWereAvailable) {
    document.dispatchEvent(new Event('rastoc:eye-features-went-available'));
  }
  if (!eyeFeatures && eyeFeatureJustWereAvailable) {
    document.dispatchEvent(new Event('rastoc:eye-features-went-unavailable'));
  }
});

document.addEventListener('rastoc:eye-features-update', ({
  detail: update,
}) => {
  if (state.calibrating) {
    // Movement detection is not performed while the system is calibrating
    return;
  }
  if (state.calibrationEyeFeatures.length === 0){
    // System is not calibrated
    return;
  }
  console.log('checking movement detection')
  // TODO: Verify whether criteria is met
  //   if last feature did not break criteria but this one does:
  //     markAsDecalibrated
  //
  //   if this feature breaks criteria but last feature met it:
  //     markAsPositionRecovered
});

window.rastoc = {
  startCalibrationPhase() {
    state.calibrating = true;

    webgazer.clearData();
    // TODO: Clear movement decalibration computed data
    state.calibrationEyeFeatures = [];
    webgazer.resume();
    webgazer.showPredictionPoints(false);

    // If this action was started by a click event (eg, clicking a start button)
    // then the events being added here will be called once. Because of that,
    // the click listeners have to be added after this click event finishes.
    // Ideally something like setImmediate could be used here but it does not
    // yet seem to be supported by most browsers.
    setTimeout(() => {
      document.addEventListener('click', _clickCalibrationHandler);

      // Enable gaze visualization after one click
      const fn = () => {
        webgazer.showPredictionPoints(true);
        document.removeEventListener('click', fn);
      };
      document.addEventListener('click', fn);

      document.dispatchEvent(new Event('rastoc:calibration-started'));
    }, 0);
  },
  endCalibrationPhase() {
    document.removeEventListener('click', _clickCalibrationHandler);
    webgazer.showPredictionPoints(false);
    // TODO: Compute movement detection criteria relevant data

    state.calibrating = false;
    document.dispatchEvent(new Event('rastoc:calibration-finished'));
  },
  get calibrationPointsCount() {
    return state.calibrationEyeFeatures.length;
  }
};
