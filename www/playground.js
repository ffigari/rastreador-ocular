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

document.addEventListener('rastoc:calibration-started', () => {
  const startButton = document.getElementById("free-calibration-start-button");
  const stopButton = document.getElementById("calibration-stop-button");
  const countElement = document.getElementById("calibrations-points-count");

  startButton.disabled = true;
  stopButton.disabled = false;
  document.getElementById(
    "calibration-status"
  ).innerHTML = "calibration in progress";
  countElement.innerHTML = "no calibration points provided";
  countElement.hidden = false;
  const ctx = document.getElementById('stillness-area').getContext('2d');
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

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
    console.log('good calibration');
    ['left', 'right'].forEach(side => {
      const ctx = document.getElementById('stillness-area').getContext('2d');
      stillnessMultiBBoxes[side].bboxes.forEach(bbox => {
        const { origin: { x, y }, width, height } = bbox;
        ctx.beginPath();
        ctx.strokeStyle = 'blue'
        ctx.fillStyle = 'blue'
        ctx.lineWidth = 1;
        ctx.rect(x, y, width, height);
        ctx.stroke();
      });
    });

    wg.showPredictionPoints(true);
    startButton.disabled = false;
    stopButton.disabled = true;
    document.getElementById("calibration-status").innerHTML = "system calibrated";
    document.removeEventListener('rastoc:point-calibrated', pointsCountUpdater);
    document.removeEventListener('rastoc:calibration-succeeded', successfulCalibrationHandler);
    document.removeEventListener('rastoc:calibration-failed', failedCalibrationHandler);
  }
  const failedCalibrationHandler = () => {
    startButton.disabled = false;
    stopButton.disabled = true;
    document.getElementById("calibration-status").innerHTML = "calibration failed";
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
    ctx.beginPath();
    ctx.strokeStyle = 'red'
    ctx.lineWidth = 4;

    const { origin: { x, y }, width, height } = lastEyesFeatures.bboxes[side];
    ctx.rect(x, y, width, height);

    ctx.stroke();
  })
})
