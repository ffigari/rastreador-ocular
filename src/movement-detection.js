const movementDetector = (function() {
  const module = {}
  const state = {
    calibrationInProgress: false,
    detectionInProgress: false,

    useNextFrameAsValidPosition: false,

    // Bounding boxes considered to be valid. They are collected during the
    // calibration phase and are then used to detect movements and whether the
    // user gets closer or further of the screen
    eyesCollectedBBoxes: [],
  }

  window.addEventListener('load', async () => {
    const model = await faceLandmarksDetection
      .load(faceLandmarksDetection.SupportedPackages.mediapipeFacemesh);
    try {
      videoStream = await navigator
        .mediaDevices
        .getUserMedia({ video: true, audio: false })
    } catch (e) {
      console.error(e)
      return
    }

    const videoElement = document.createElement('video')
    videoElement.srcObject = videoStream
    videoElement.play()
    videoElement.addEventListener('canplay', () => {
      const detectorLoop = async () => {
        const predictions = await model.estimateFaces({
          input: videoElement
        })
        if (predictions.length === 0) {
          throw new Error('No se detectó ninguna cara.')
        }
        if (predictions.length > 1) {
          throw new Error('Se detectó más de una cara.')
        }
        const [leftBBox, rightBBox] = [
          [189, 244, 232, 230, 228, 226, 225, 223, 221],
          [413, 464, 452, 450, 448, 446, 445, 443, 441],
        ].map(keypointIndexes => {
          const min = { x: null, y: null }
          const max = { x: null, y: null };
          keypointIndexes.forEach(keypointIndex => {
            const [x, y, z] = predictions[0].scaledMesh[keypointIndex];
            min.x = min.x && min.x < x ? min.x : x
            min.y = min.y && min.y < y ? min.y : y
            max.x = max.x && max.x > x ? max.x : x
            max.y = max.y && max.y > y ? max.y : y
          })
          return { min, max }
        })

        if (state.useNextFrameAsValidPosition) {
          state.eyesCollectedBBoxes.push({
            left: leftBBox,
            right: rightBBox,
          })
          state.useNextFrameAsValidPosition = false
        }

        // TODO: Detectar movimiento
        //       Movimientos laterales, up/down, alejación, acercación
        if (state.calibrationInProgress || state.detectionInProgress) {
          window.requestAnimationFrame(detectorLoop)
        }
      }
      Object.assign(module, {
        // TODO: Agregar interfaz para debuggear
        //       Debería poder pasarle algún elemento HTML (canvas? video?)
        //       donde se visualice la info que se va capturando.
        videoStream,
        useNextFrameAsValidPosition() {
          if (!state.calibrationInProgress) {
            throw new Error(
              'Sólo se pueden agregar puntos durante la fase de calibración.'
            )
          }
          state.useNextFrameAsValidPosition = true;
        },
        start: {
          calibration() {
            state.calibrationInProgress = true
            state.detectionInProgress = false
            state.eyesCollectedBBoxes = []
            window.requestAnimationFrame(detectorLoop)
          },
          detection() {
            state.detectionInProgress = true
            state.calibrationInProgress = false
          }
        },
        stop() {
          state.calibrationInProgress = false
          state.detectionInProgress = false
        },
      })
      document.dispatchEvent(new Event('movement-detector:ready'))
    })
  })

  return module
})()
