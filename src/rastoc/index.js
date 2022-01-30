class Point {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
}

class BBox {
  constructor(origin, width, height) {
    this.origin = origin;
    this.width = width;
    this.height = height;
  }
  static createResized(bbox, scalingFactor) {
    return new BBox(
      bbox.origin,
      bbox.width * scalingFactor,
      bbox.height * scalingFactor
    );
  }
  contains(point) {
    // TODO: Implement this
    return true;
  }
  get corners() {
    // TODO: Implement this
    return [];
  }
}

class MultiBBox {
  constructor(bboxes) {
    if (bboxes.length === 0) {
      throw new Error(
        `Can not create a multi bbox without bboxes.`
      );
    }
    this.bboxes = bboxes;
  }
  contains(inputBBox) {
    return inputBBox.corners.every((
      corner
    ) => this.bboxes.some(bbox => bbox.contains(corner)));
  }
} 

class EyesFeatures {
  constructor(bboxes) {
    this.bboxes = {};
    ['left', 'right'].forEach(side => {
      this.bboxes[side] = bboxes[side];
    })
  }
  static fromWGEyesFeatures(wgEyesFeature) {
    const bboxes = {};
    ['left', 'right'].forEach(side => {
      const {
        imagex, imagey, width, height
      } = wgEyesFeature[side];
      bboxes[side] = new BBox(
        new Point(imagex, imagey),
        width,
        height
      );
    })
    return new EyesFeatures(bboxes);
  }
}

class StillnessChecker {
  constructor(eyesFeatures) {
    this.stillnessMultiBBoxes = {};
    ['left', 'right'].forEach(side => {
      this.stillnessMultiBBoxes[side] = new MultiBBox(eyesFeatures
        .filter(ftr => !!ftr[side])
        .map(ftr => ftr[side])
        .map((bbox) => BBox.createResized(bbox, 1.3))
      )
    });
  }
  areEyesInOriginalPosition(eyesFeatures) {
    return ['left', 'right'].every((
      side
    ) => this.stillnessMultiBBoxes[side].contains(eyesFeatures[side]));
  }
}

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
  lastFrameEyesFeatures: null,
  stillnessChecker: null,
};

const _clickCalibrationHandler = ({ clientX: x, clientY: y }) => {
  if (!state.lastFrameEyesFeatures) {
    console.log('Calibration was not performed due to missing eye features.');
    return;
  }
  webgazer.recordScreenPosition(x, y, 'click');
  state.calibrationEyeFeatures.push(state.lastFrameEyesFeatures);
  document.dispatchEvent(new Event('rastoc:point-calibrated'));
};

// TODO: This could be placed in a separate file dedicated to webgazer wrapper
//       related stuff.
document.addEventListener('webgazer:eye-features-update', ({
  detail: wgEyesFeature,
}) => {
  const eyeFeaturesJustWereAvailable = !!state.lastFrameEyesFeatures;
  state.lastFrameEyesFeatures = null;
  if (wgEyesFeature) {
    const eyesFeatures = EyesFeatures.fromWGEyesFeatures(wgEyesFeature);
    console.log(eyesFeatures.bboxes.left, eyesFeatures.bboxes['left'])
    state.lastFrameEyesFeatures = eyesFeatures;
    document.dispatchEvent(new CustomEvent('rastoc:eye-features-update', {
      detail: eyesFeatures,
    }))
  }

  if (wgEyesFeature && !eyeFeaturesJustWereAvailable) {
    document.dispatchEvent(new Event('rastoc:eye-features-went-available'));
  }
  if (!wgEyesFeature && eyeFeaturesJustWereAvailable) {
    document.dispatchEvent(new Event('rastoc:eye-features-went-unavailable'));
  }
});

document.addEventListener('rastoc:eye-features-update', ({
  detail: eyesFeatures,
}) => {
  if (!state.stillnessChecker) {
    return;
  }

  // TODO: Compare this frame stillness against the previous frame stillness
  //            if face moved out or in the valid positions then inform it with
  //            two distinct events
  console.log(state.stillnessChecker.areEyesInOriginalPosition(eyesFeatures))
});

window.rastoc = {
  startCalibrationPhase() {
    webgazer.clearData();
    state.stillnessChecker = null;
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

    state.stillnessChecker = new StillnessChecker(state.calibrationEyeFeatures);

    // TODO: Mark movement as not detected
    // TODO: Draw stillness MultiBBoxes
    document.dispatchEvent(new Event('rastoc:calibration-finished'));
  },
  get calibrationPointsCount() {
    return state.calibrationEyeFeatures.length;
  }
};
