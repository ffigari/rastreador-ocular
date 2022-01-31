class Point {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
  add(xDelta, yDelta) {
    return new Point(this.x + xDelta, this.y + yDelta);
  }
}

class BBox {
  constructor(origin, width, height) {
    this.origin = origin;  // `origin` is the top left coordinate of the bbox,
                           //  not the center of it
    this.width = width;
    this.height = height;
  }
  get center() {
    return this.origin
      .add(
        Math.round(this.width / 2),
        Math.round(this.height / 2)
      );
  }
  static createResizedFromCenter(bbox, scalingFactor) {
    const { width, height } = bbox;
    const newOrigin = bbox.center.add(
        -(Math.round(scalingFactor * width / 2)),
        -(Math.round(scalingFactor * height / 2))
      );
    return new BBox(
      newOrigin,
      width * scalingFactor,
      height * scalingFactor
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

      console.log(BBox)
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
  // list of features corresponding to the ones from last frame each time a
  // calibration point was added
  calibrationEyesFeatures: [],
  // eye features from last frame
  lastFrameEyesFeatures: null,
  // TODO: This two variables have different goals (movement detection related)
  correctlyCalibrated: false,
  calibrated: false,
};

const _clickCalibrationHandler = ({ clientX: x, clientY: y }) => {
  if (!state.lastFrameEyesFeatures) {
    console.log('Calibration was not performed due to missing eye features.');
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

const startMovementDetection = (stillnessChecker) => {
  const frameHandler = ({ detail: eyesFeatures }) => {
    if (!state.calibrated) {
      return;
    }
    console.log('last eyes still?', stillnessChecker.areEyesInOriginalPosition(eyesFeatures))
    // TODO: Compare this frame stillness against the previous frame stillness
    //            if face moved out or in the valid positions then inform it with
    //            two distinct events
  }
  document.addEventListener('rastoc:eye-features-update', frameHandler);
  const finishUpHandler = () => {
    document.removeEventListener('rastoc:eye-features-update', frameHandler);
    document.removeEventListener('rastoc:resetting-calibration', finishUpHandler);
  }
  document.addEventListener('rastoc:resetting-calibration', finishUpHandler);
}

window.rastoc = {
  startCalibrationPhase() {
    state.correctlyCalibrated = false;
    state.calibrated = false;
    document.dispatchEvent(new Event('rastoc:resetting-calibration'));
    webgazer.clearData();
    state.calibrationEyesFeatures = [];
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

    let stillnessChecker;
    try {
      stillnessChecker = new StillnessChecker(state.calibrationEyesFeatures);
      console.log(stillnessChecker)
      state.correctlyCalibrated = true;
      state.calibrated = true;
    } catch (e) {
      console.error('calibration failed:', e);
      state.correctlyCalibrated = false;
      state.calibrated = false;
    }

    if (state.correctlyCalibrated) {
      startMovementDetection(stillnessChecker);
      document.dispatchEvent(new CustomEvent('rastoc:calibration-succeeded', {
        detail: {
          stillnessMultiBBoxes: stillnessChecker.stillnessMultiBBoxes,
        },
      }));
    } else {
      document.dispatchEvent(new Event('rastoc:calibration-failed'));
    }
  },
  get isCorrectlyCalibrated() {
    // TODO: This value should be updated on each frame using the stillnessChecker
    return state.correctlyCalibrated;
  },
  get calibrationPointsCount() {
    return state.calibrationEyesFeatures.length;
  }
};
