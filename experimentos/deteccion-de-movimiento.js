document.addEventListener('movement-detector:ready', () => {
  const videoElement = document.getElementById('webcam-output')
  videoElement.srcObject = movementDetector.videoStream
  videoElement.play()

  const calibrationStarterButton = document.getElementById('calibration-starter')
  const adderButton = document.getElementById('valid-position-adder')
  const detectionStarterButton = document.getElementById('detection-starter')
  const stoperButton = document.getElementById('detector-stoper')

  calibrationStarterButton.disabled = false
  calibrationStarterButton.addEventListener('click', () => {
    movementDetector.start.calibration()
    calibrationStarterButton.disabled = true
    adderButton.disabled = false
    detectionStarterButton.disabled = false
    stoperButton.disabled = false
    document.getElementById('calibration-instructions').hidden = false
  })
  adderButton.addEventListener('click', () => {
    movementDetector.useNextFrameAsValidPosition()
  })
  detectionStarterButton.addEventListener('click', () => {
    movementDetector.start.detection()
    calibrationStarterButton.disabled = true
    adderButton.disabled = true
    detectionStarterButton.disabled = true
    stoperButton.disabled = false
    document.getElementById('calibration-instructions').hidden = true
  })
  stoperButton.addEventListener('click', () => {
    movementDetector.stop()
    calibrationStarterButton.disabled = false
    adderButton.disabled = true
    detectionStarterButton.disabled = true
    stoperButton.disabled = true
    document.getElementById('calibration-instructions').hidden = true
  })
})
