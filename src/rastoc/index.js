import { Point, BBox, MultiBBox } from '../types/index.js';

class EyesFeatures {
  constructor(bboxes) {
    this.bboxes = {
      left: bboxes.left,
      right: bboxes.right,
    }
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
  constructor(calibrationEyesFeatures) {
    const calibrationBBoxes = calibrationEyesFeatures.map(ef => ef.bboxes)

    this.stillnessMultiBBoxes = {};
    ['left', 'right'].forEach(side => {
      const sideBBoxes = calibrationBBoxes.map(ftr => ftr[side]).filter(x => !!x);
      if (sideBBoxes.length === 0) {
        throw new Error(`Missing bboxes for ${side} eye.`);
      }

      this.stillnessMultiBBoxes[side] = new MultiBBox(sideBBoxes.map((
        bbox
      ) => BBox.createResizedFromCenter(bbox, 1.8)));
    });
  }
  areEyesInOriginalPosition(eyesFeatures) {
    return ['left', 'right'].every((
      side
    ) => this.stillnessMultiBBoxes[side].contains(eyesFeatures.bboxes[side]));
  }
}

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
  calibrating: false,
  // list of features corresponding to the ones from last frame each time a
  // calibration point was added
  calibrationEyesFeatures: [],
  // eye features from last frame
  lastFrameEyesFeatures: null,
  calibrationIsNeeded: true,
};

const mapCoordinateToGaze = ({ x, y }) => {
  if (!state.calibrating) {
    console.warn('Can not calibrate outside of calibration phases');
    return;
  }
  if (!state.lastFrameEyesFeatures) {
    console.warn('Calibration was not performed due to missing eye features.');
    return;
  }
  webgazer.recordScreenPosition(x, y, 'click');
  state.calibrationEyesFeatures.push(state.lastFrameEyesFeatures);
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

const startDecalibrationCriteriaCheck = () => {
  state.calibrationIsNeeded = false;
  const decalibrationDetectedHandler = () => {
    state.calibrationIsNeeded = true;
    document.removeEventListener('rastoc:stillness-position-lost', decalibrationDetectedHandler);
    document.removeEventListener('rastoc:resetting-calibration', calibrationResetHandler);
    document.dispatchEvent(new Event('rastoc:decalibration-detected'));
  };
  const calibrationResetHandler = () => {
    state.calibrationIsNeeded = true;
    document.removeEventListener('rastoc:stillness-position-lost', decalibrationDetectedHandler);
    document.removeEventListener('rastoc:resetting-calibration', calibrationResetHandler);
  };
  document.addEventListener('rastoc:stillness-position-lost', decalibrationDetectedHandler);
  document.addEventListener('rastoc:resetting-calibration', calibrationResetHandler);
};

const startMovementDetection = (stillnessChecker) => {
  let calibrationLost = false;
  let previousFrameWasOutOfPlace = false;
  const frameHandler = ({ detail: eyesFeatures }) => {
    const currentFrameIsOutOfPlace = !stillnessChecker.areEyesInOriginalPosition(
      eyesFeatures
    );

    if (previousFrameWasOutOfPlace && !currentFrameIsOutOfPlace) {
      document.dispatchEvent(new Event('rastoc:stillness-position-recovered'));
    } else if (!previousFrameWasOutOfPlace && currentFrameIsOutOfPlace) {
      document.dispatchEvent(new Event('rastoc:stillness-position-lost'));
    }
    previousFrameWasOutOfPlace = currentFrameIsOutOfPlace;
  }
  document.addEventListener('rastoc:eye-features-update', frameHandler);
  const finishUpHandler = () => {
    document.removeEventListener('rastoc:eye-features-update', frameHandler);
    document.removeEventListener('rastoc:resetting-calibration', finishUpHandler);
  }
  document.addEventListener('rastoc:resetting-calibration', finishUpHandler);
}

const showGazeEstimation = () => {
  webgazer.showPredictionPoints(true);
}
const hideGazeEstimation = () => {
  webgazer.showPredictionPoints(false);
}

const clickToGazeCalibrationHandler = ({ clientX, clientY }) => {
  mapCoordinateToGaze({
    x: clientX,
    y: clientY,
  })
};

window.rastoc = {
  showGazeEstimation,
  hideGazeEstimation,
  startCalibrationPhase(calibrationType) {
    calibrationType = calibrationType || "click";
    if (!["click", "external"].includes(calibrationType)) {
      throw new Error(`calibration type (${calibrationType}) is not valid.`);
    }

    state.calibrating = true;
    document.dispatchEvent(new Event('rastoc:resetting-calibration'));
    webgazer.clearData();
    state.calibrationEyesFeatures = [];
    webgazer.resume();
    hideGazeEstimation();

    // If this action was started by a click event (eg, clicking a start button)
    // then the events being added here will be called once. Because of that,
    // the click listeners have to be added after this click event finishes.
    // Ideally something like setImmediate could be used here but it does not
    // yet seem to be supported by most browsers.
    setTimeout(() => {
      if (calibrationType === "click") {
        document.addEventListener('click', clickToGazeCalibrationHandler);
      }

      // Enable gaze visualization after one click
      const fn = () => {
        showGazeEstimation();
        document.removeEventListener('click', fn);
      };
      document.addEventListener('click', fn);

      document.dispatchEvent(new Event('rastoc:calibration-started'));
    }, 0);

    let res;
    if (calibrationType === "external") {
      res = ({ x, y }) => {
        mapCoordinateToGaze(new Point(x, y));
      };
    }
    return res;
  },
  endCalibrationPhase(calibrationType) {
    calibrationType = calibrationType || "click";
    if (!["click", "external"].includes(calibrationType)) {
      throw new Error(`calibration type (${calibrationType}) is not valid.`);
    }

    if (calibrationType === "click") {
      document.removeEventListener('click', clickToGazeCalibrationHandler);
    }

    hideGazeEstimation();

    let stillnessChecker;
    let correctlyCalibrated = false;
    try {
      stillnessChecker = new StillnessChecker(state.calibrationEyesFeatures);
      correctlyCalibrated = true;
    } catch (e) {
      console.error('calibration failed:', e);
    }

    if (correctlyCalibrated) {
      startMovementDetection(stillnessChecker);
      startDecalibrationCriteriaCheck();
      document.dispatchEvent(new CustomEvent('rastoc:calibration-succeeded', {
        detail: {
          stillnessMultiBBoxes: stillnessChecker.stillnessMultiBBoxes,
        },
      }));
    } else {
      document.dispatchEvent(new Event('rastoc:calibration-failed'));
    }
    state.calibrating = false;
  },
  get isCorrectlyCalibrated() {
    return !state.calibrationIsNeeded;
  },
  get calibrationPointsCount() {
    return state.calibrationEyesFeatures.length;
  },
};
