let wg;
document.addEventListener('DOMContentLoaded', async () => {
  if (typeof webgazer === 'undefined' || !window.webgazer) {
    console.error(
      'WebGazer was not found. Make sure the js file has been loaded.'
    );
    document.dispatchEvent(new Event('webgazer-not-found'));
    return;
  }
  wg = window.webgazer;
  document.dispatchEvent(new Event('webgazer-found'));
})

document.addEventListener('webgazer-not-found', () => {
  wgUnavailabilityMsg = document.createElement('p');
  wgUnavailabilityMsg.innerHTML = "WebGazer not found";
  document.getElementById('debugging-webcam-video-container').append(wgUnavailabilityMsg);
  document.getElementById('webgazer-loading-status').remove();
});

document.addEventListener('webgazer-found', async () => {
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
