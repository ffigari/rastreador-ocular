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

  const eyesBBoxesCanvas = document.getElementById('eye-bboxes')
  eyesBBoxesCanvas.hidden = false;
  eyesBBoxesCanvas.style.position = 'absolute';

  const faceFeedbackCanvas = document.getElementById('webgazerFaceFeedbackBox');
  faceFeedbackCanvas.style.position = 'relative';

  const wgWebcamVideoCanvas = document.getElementById('webgazerFaceOverlay');
  eyesBBoxesCanvas.width = wgWebcamVideoCanvas.width;
  eyesBBoxesCanvas.height = wgWebcamVideoCanvas.height;
  eyesBBoxesCanvas.style.width = wgWebcamVideoCanvas.style.width
  eyesBBoxesCanvas.style.height = wgWebcamVideoCanvas.style.height
  eyesBBoxesCanvas.style.transform = 'scale(-1, 1)';

  const fn = () => {
    document.getElementById("free-calibration-start-button").disabled = false;
    document.removeEventListener('rastoc:eye-features-went-available', fn)
  }
  document.addEventListener('rastoc:eye-features-went-available', fn);
});

document.addEventListener('rastoc:point-calibrated', () => {
  const pointsCount = rastoc.calibrationPointsCount;
  document.getElementById(
    "calibration-status"
  ).innerHTML = `calibrated (${ pointsCount === 1
    ? "1 point"
    : `${pointsCount} points`
  })`;
});

document.addEventListener('rastoc:calibration-started', () => {
  document.getElementById("free-calibration-start-button").disabled = true;
  document.getElementById("calibration-stop-button").disabled = false;
  document.getElementById("calibration-status").innerHTML = "uncalibrated"
});

document.addEventListener('rastoc:calibration-finished', () => {
  document.getElementById("free-calibration-start-button").disabled = false;
  document.getElementById("calibration-stop-button").disabled = true;
});

document.addEventListener('rastoc:eye-features-went-available', () => {
  document.getElementById('eye-features-status').innerHTML = "available"
  wg.showFaceOverlay(true);
});

document.addEventListener('rastoc:eye-features-went-unavailable', () => {
  document.getElementById('eye-features-status').innerHTML = "unavailable"
  const eyesBBoxesCanvas = document.getElementById('eye-bboxes');
  const ctx = eyesBBoxesCanvas.getContext('2d');
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  wg.showFaceOverlay(false);
});

document.addEventListener('rastoc:eye-features-update', ({
  detail: lastEyeFeature,
}) => {
  const eyesBBoxesCanvas = document.getElementById('eye-bboxes');

  const ctx = eyesBBoxesCanvas.getContext('2d');
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

  ['left', 'right'].forEach((side) => {
    ctx.beginPath();
    ctx.strokeStyle = 'red'
    ctx.lineWidth = 4;

    const { origin: { x, y }, width, height } = lastEyeFeature[side];
    ctx.rect(x, y, width, height);

    ctx.stroke();
  })
})
