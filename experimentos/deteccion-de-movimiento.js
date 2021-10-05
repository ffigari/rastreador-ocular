document.addEventListener('movement-detector:module-ready', () => {
  movementDetector.visualizeAt(document.getElementById('debugging-canvas'))

  const calibrationStarterButton = document.getElementById('calibration-starter')
  const adderButton = document.getElementById('valid-position-adder')
  const detectionStarterButton = document.getElementById('detection-starter')
  const reseterButton = document.getElementById('reseter')

  calibrationStarterButton.addEventListener('click', () => {
    calibrationStarterButton.disabled = true
    movementDetector.start.calibration()
    adderButton.disabled = false
    reseterButton.disabled = false
    document.getElementById('calibration-instructions').hidden = false
  })
  adderButton.addEventListener('click', () => {
    movementDetector.useNextFrameAsValidPosition()
  })
  document.addEventListener('movement-detector:calibration-ready', () => {
    detectionStarterButton.disabled = false;
  })
  detectionStarterButton.addEventListener('click', () => {
    adderButton.disabled = true
    document.getElementById('calibration-instructions').hidden = true
    detectionStarterButton.disabled = true
    movementDetector.start.detection()
  })
  reseterButton.addEventListener('click', () => {
    adderButton.disabled = true;
    detectionStarterButton.disabled = true;
    reseterButton.disabled = true;
    movementDetector.stop()
    calibrationStarterButton.disabled = false;
  })

  calibrationStarterButton.disabled = false
})
