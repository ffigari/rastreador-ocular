const setUp = {
  debugging() {
    rastoc.debugFaceAt(document.getElementById('debugging-canvas'));
  },
  controllers() {
    const calibrationStarterButton = document.getElementById('calibration-starter')
    const adderButton = document.getElementById('valid-position-adder')
    const detectionStarterButton = document.getElementById('detection-starter')
    const reseterButton = document.getElementById('reseter')

    calibrationStarterButton.addEventListener('click', () => {
      calibrationStarterButton.disabled = true
      rastoc.movementDetector.start.calibration()
      adderButton.disabled = false
      reseterButton.disabled = false
      document.getElementById('calibration-instructions').hidden = false
    })
    adderButton.addEventListener('click', () => {
      rastoc.movementDetector.useNextFrameAsValidPosition()
    })
    document.addEventListener('rastoc_movement-detector:calibration:ready', () => {
      detectionStarterButton.disabled = false;
    })
    detectionStarterButton.addEventListener('click', () => {
      adderButton.disabled = true
      document.getElementById('calibration-instructions').hidden = true
      detectionStarterButton.disabled = true
      rastoc.movementDetector.start.detection()
    })
    reseterButton.addEventListener('click', () => {
      adderButton.disabled = true;
      detectionStarterButton.disabled = true;
      reseterButton.disabled = true;
      rastoc.movementDetector.stop()
      calibrationStarterButton.disabled = false;
    })

    calibrationStarterButton.disabled = false
  },
  faceReporter() {
    const hideAllBut = (id) => {
      document.getElementById('face-ok-msg').hidden = true;
      document.getElementById('no-face-msg').hidden = true;
      document.getElementById('multiple-faces-msg').hidden = true;
      document.getElementById(id).hidden = false;
    }
    document.addEventListener(
      'rastoc_movement-detector:face:detected-correctly',
      () => hideAllBut('face-ok-msg')
    );
    document.addEventListener(
      'rastoc_movement-detector:face:not-detected',
      () => hideAllBut('no-face-msg')
    );
    document.addEventListener(
      'rastoc_movement-detector:face:detected-multiple-times',
      () => hideAllBut('multiple-faces-msg')
    );
  },
  movementReporter() {
    const hideAll = () => {
      document.getElementById('no-movement-msg').hidden = true;
      document.getElementById('movement-detected-msg').hidden = true;
    }
    const hideAllBut = (id) => {
      hideAll();
      document.getElementById(id).hidden = false;
    }
    document.addEventListener(
      'rastoc_movement-detector:movement:not-detected',
      () => hideAllBut('no-movement-msg')
    );
    document.addEventListener(
      'rastoc_movement-detector:movement:detected',
      () => hideAllBut('movement-detected-msg')
    );
    document.addEventListener(
      'rastoc_movement-detector:calibration:reset',
      hideAll
    )

    const distanceUpdater = () => {
      document.getElementById("distance-container").innerHTML =
        rastoc.movementDetector.distanceToValidPosition()?.toFixed(2) || "null"
      window.requestAnimationFrame(distanceUpdater);
    };
    window.requestAnimationFrame(distanceUpdater);
  },
}
document.addEventListener('rastoc_movement-detector:ready', () => {
  setUp.debugging();
  setUp.controllers();
  setUp.faceReporter();
  setUp.movementReporter();
})
