const wg = window.webgazer;

document.addEventListener('rastoc:webgazer-not-found', () => {
  wgUnavailabilityMsg = document.createElement('p');
  wgUnavailabilityMsg.innerHTML = "WebGazer not found";
  document.getElementById('visual-debugging-container').append(wgUnavailabilityMsg);
  document.getElementById('webgazer-loading-status').remove();
});

document.addEventListener('rastoc:webgazer-found', async () => {
  wg.showVideo(false);
  wg.showFaceOverlay(false);
  wg.showFaceFeedbackBox(false);
  wg.showPredictionPoints(false);

  const startButtonInitialEnable = () => {
    document.getElementById("free-calibration-start-button").disabled = false;
    document.removeEventListener('rastoc:eye-features-went-available', startButtonInitialEnable)
  }
  document.addEventListener('rastoc:eye-features-went-available', startButtonInitialEnable);
  await wg.begin(undefined, {
    initializeMouseListeners: false,
  });
  wg.showVideo(true);
  wg.showFaceFeedbackBox(true);
  document.getElementById('webgazer-loading-status').remove();

  const visualDebuggingContainer = document.getElementById(
    "visual-debugging-container"
  );
  const wgVisualAid = document.getElementById("webgazerVideoContainer");
  visualDebuggingContainer.prepend(wgVisualAid);
  wgVisualAid.style.position = 'absolute';
  wgVisualAid.style.top = '';
  wgVisualAid.style.left = '';

  const faceFeedbackCanvas = document.getElementById('webgazerFaceFeedbackBox');
  faceFeedbackCanvas.style.position = 'relative';

  const wgWebcamVideoCanvas = document.getElementById('webgazerFaceOverlay');
  ['eye-bboxes', 'stillness-area'].forEach(canvasId => {
    const canvas = document.getElementById(canvasId)
    canvas.hidden = false;
    canvas.style.position = 'absolute';
    canvas.width = wgWebcamVideoCanvas.width;
    canvas.height = wgWebcamVideoCanvas.height;
    canvas.style.width = wgWebcamVideoCanvas.style.width
    canvas.style.height = wgWebcamVideoCanvas.style.height
    canvas.style.transform = 'scale(-1, 1)';
  })
});

const startDecalibrationReport = (calibrationStatusMsg) => {
  const decalibrationDetectedHandler = () => {
    calibrationStatusMsg.innerHTML = "decalibration detected";
    document.removeEventListener('rastoc:decalibration-detected', decalibrationDetectedHandler);
    document.removeEventListener('rastoc:resetting-calibration', calibrationResetHandler);
  };
  const calibrationResetHandler = () => {
    document.removeEventListener('rastoc:decalibration-detected', decalibrationDetectedHandler);
    document.removeEventListener('rastoc:resetting-calibration', calibrationResetHandler);
  };
  document.addEventListener('rastoc:decalibration-detected', decalibrationDetectedHandler)
  document.addEventListener('rastoc:resetting-calibration', calibrationResetHandler);
}

const startMovementReport = (stillnessMultiBBoxes) => {
  const movementStatusMsg = document.getElementById("movement-detection-status");
  const movementStatusReport = document.getElementById("movement-detection-report");
  const movedOnceMsg = document.getElementById("moved-once");

  const ctx = document.getElementById('stillness-area').getContext('2d');
  ctx.globalAlpha = 0.1;
  ['left', 'right'].forEach(side => {
    stillnessMultiBBoxes[side].bboxes.forEach(bbox => {
      const { origin: { x, y }, width, height } = bbox;
      ctx.fillStyle = 'blue';
      ctx.fillRect(x, y, width, height);
    });
  });
  ctx.globalAlpha = 1;
  movementStatusMsg.innerHTML = "movement detection enabled";
  movementStatusReport.style.visibility = "visible";

  movedOnceMsg.innerHTML = "no";
  const firstMoveHandler = () => {
    movedOnceMsg.innerHTML = "yes";
    document.removeEventListener('rastoc:stillness-position-lost', firstMoveHandler);
  };
  document.addEventListener('rastoc:stillness-position-lost', firstMoveHandler);

  const faceStatusMsg = document.getElementById("eyes-status");
  faceStatusMsg.innerHTML = "no eyes movement detected";
  const stillnessRecoveredHandler = () => {
    faceStatusMsg.innerHTML = "eyes moved but went back to original position";
  }
  const stillnessLostHandler = () => {
    faceStatusMsg.innerHTML = "eyes moved";
  }
  document.addEventListener('rastoc:stillness-position-recovered', stillnessRecoveredHandler);
  document.addEventListener('rastoc:stillness-position-lost', stillnessLostHandler);

  const restartedCalibrationHandler = () => {
    movementStatusMsg.innerHTML = "movement detection disabled";
    const ctx = document.getElementById('stillness-area').getContext('2d');
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    movementStatusReport.style.visibility = "hidden";

    document.removeEventListener('rastoc:stillness-position-recovered', stillnessRecoveredHandler);
    document.removeEventListener('rastoc:stillness-position-lost', stillnessLostHandler);
    document.removeEventListener('rastoc:calibration-started', restartedCalibrationHandler);
  }
  document.addEventListener('rastoc:calibration-started', restartedCalibrationHandler);
};

document.addEventListener('rastoc:calibration-started', () => {
  const startButton = document.getElementById("free-calibration-start-button");
  const stopButton = document.getElementById("calibration-stop-button");
  const countElement = document.getElementById("calibrations-points-count");
  const calibrationStatusMsg = document.getElementById("calibration-status");

  startButton.disabled = true;
  stopButton.disabled = false;
  calibrationStatusMsg.innerHTML = "calibration in progress";
  countElement.innerHTML = "no calibration points provided";
  countElement.hidden = false;

  // Update info on added points after each calibration
  const pointsCountUpdater = () => {
    const pointsCount = rastoc.calibrationPointsCount;
    document.getElementById(
      "calibrations-points-count"
    ).innerHTML = `calibrated (${ pointsCount === 1
      ? "1 point"
      : `${pointsCount} points`
    })`;
  };
  document.addEventListener('rastoc:point-calibrated', pointsCountUpdater);

  // Set up post calibration handlers
  const successfulCalibrationHandler = ({ detail: {
    stillnessMultiBBoxes
  } }) => {
    rastoc.showGazeEstimation();
    startButton.disabled = false;
    stopButton.disabled = true;
    calibrationStatusMsg.innerHTML = "system calibrated";

    startMovementReport(stillnessMultiBBoxes);
    startDecalibrationReport(calibrationStatusMsg);

    document.removeEventListener('rastoc:point-calibrated', pointsCountUpdater);
    document.removeEventListener('rastoc:calibration-succeeded', successfulCalibrationHandler);
    document.removeEventListener('rastoc:calibration-failed', failedCalibrationHandler);
  }
  const failedCalibrationHandler = () => {
    startButton.disabled = false;
    stopButton.disabled = true;
    calibrationStatusMsg.innerHTML = "calibration failed";
    document.removeEventListener('rastoc:point-calibrated', pointsCountUpdater);
    document.removeEventListener('rastoc:calibration-succeeded', successfulCalibrationHandler);
    document.removeEventListener('rastoc:calibration-failed', failedCalibrationHandler);
  };
  document.addEventListener('rastoc:calibration-succeeded', successfulCalibrationHandler);
  document.addEventListener('rastoc:calibration-failed', failedCalibrationHandler);
});

document.addEventListener('rastoc:eye-features-went-available', () => {
  document.getElementById(
    'eye-features-status'
  ).innerHTML = "eye features available";
  wg.showFaceOverlay(true);
});

document.addEventListener('rastoc:eye-features-went-unavailable', () => {
  document.getElementById(
    'eye-features-status'
  ).innerHTML = "eye features unavailable";
  const eyesBBoxesCanvas = document.getElementById('eye-bboxes');
  const ctx = eyesBBoxesCanvas.getContext('2d');
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  wg.showFaceOverlay(false);
});

document.addEventListener('rastoc:eye-features-update', ({
  detail: lastEyesFeatures,
}) => {
  const eyesBBoxesCanvas = document.getElementById('eye-bboxes');

  const ctx = eyesBBoxesCanvas.getContext('2d');
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  ['left', 'right'].forEach((side) => {
    const { origin: { x, y }, width, height } = lastEyesFeatures.bboxes[side];
    ctx.globalAlpha = 0.4;
    ctx.fillStyle = 'red';
    ctx.fillRect(x, y, width, height);
    ctx.globalAlpha = 1;
  })
})
