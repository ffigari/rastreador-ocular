const wg = window.webgazer;

document.addEventListener('rastoc:webgazer-not-found', () => {
  wgUnavailabilityMsg = document.createElement('p');
  wgUnavailabilityMsg.innerHTML = "WebGazer not found";
  document.getElementById('debugging-webcam-video-container').append(wgUnavailabilityMsg);
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
  wg.showFaceOverlay(true);
  wg.showFaceFeedbackBox(true);
  document.getElementById(
    "debugging-webcam-video-container"
  ).append(document.getElementById("webgazerVideoContainer"));
  document.getElementById(
    'webgazerVideoContainer'
  ).style.removeProperty('position');
  document.getElementById(
    'webgazerFaceFeedbackBox'
  ).style.position = 'relative';
  document.getElementById('webgazer-loading-status').remove();

  document.getElementById("free-calibration-start-button").disabled = false;
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
});

document.addEventListener('rastoc:eye-features-went-unavailable', () => {
  document.getElementById('eye-features-status').innerHTML = "unavailable"
});
