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

// TODO: Subscribe to WG's eye patches update and draw them over the debugging
//       canvas that has the video
// TODO: Reimplement movement detection by reusing WG eye patches

const state = {
  calibrationPointsCount: 0,
  eyeFeaturesJustWereAvailable: false,
};

const _mapCoordinateToGaze = (x, y) => {
  // TODO: Add gaze position as valid movement detection position
  webgazer.recordScreenPosition(x, y, 'click');
  state.calibrationPointsCount++;
  document.dispatchEvent(new Event('rastoc:point-calibrated'));
};
const _clickCalibrationHandler = ({ clientX, clientY }) => {
  _mapCoordinateToGaze(clientX, clientY);
};
const startCalibrationPhase = () => {
  webgazer.clearData();
  // TODO: Reset movement detection data
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
};
const endCalibrationPhase = () => {
  document.removeEventListener('click', _clickCalibrationHandler);
  webgazer.showPredictionPoints(false);
  document.dispatchEvent(new Event('rastoc:calibration-finished'));
};

document.addEventListener('webgazer:eye-features-update', ({
  detail: lastEyeFeatures,
}) => {
  state.lastEyeFeatures = lastEyeFeatures
  if (lastEyeFeatures) {
    document.dispatchEvent(new CustomEvent('rastoc:eye-features-update', {
      detail: {},
    }))
  }

  document.dispatchEvent(new Event('rastoc:eye-features-updated'))
  if (lastEyeFeatures && !state.eyeFeaturesJustWereAvailable) {
    state.eyeFeaturesJustWereAvailable = true;
    document.dispatchEvent(new Event('rastoc:eye-features-went-available'));
  }
  if (!lastEyeFeatures && state.eyeFeaturesJustWereAvailable) {
    state.eyeFeaturesJustWereAvailable = false;
    document.dispatchEvent(new Event('rastoc:eye-features-went-unavailable'));
  }
});

// TODO: Add movement detection
//        . draw eye patches over video canvas for debugging purposes
//          . if eye patch is not present then it should be informed in the
//            status
//        . on point-calibration:
//          - if eye patch is not present, inform it and prevent calibration
//          - compute eyes valid position info from last relevant eye patch
//            (bbox or center, width and height?)
//        . on calibration start
//          . reset movement detection
//        . on calibration end
//          . enable movement detection
//        . on eye patch update
//          . if calibration is enabled then compute where movement detection
//            criteria is met. If movement status (detected or not) changes,
//            then inform it.
//        . on movement detection
//          . mark as decalibrated
window.rastoc = {
  startCalibrationPhase,
  endCalibrationPhase,
  get calibrationPointsCount() {
    return state.calibrationPointsCount;
  }
};
