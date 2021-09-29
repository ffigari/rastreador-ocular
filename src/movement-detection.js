

const movementDetector = (function() {
  const module = {}
  const state = {
    calibrationInProgress: false,
    detectionInProgress: false,

    useNextFrameAsValidPosition: false,

    lastCapturedEyes: null,

    // Eye patches considered to be valid positions. They are collected during
    // the calibration phase and are then used to detect movements and whether
    // the user gets closer or further of the screen.
    collectedEyesPatches: [],

    // Canvas element in which the movement detection should be debugged.
    // Captured video and estimated data will be drawn over it.
    debuggingCanvasCtx: null,
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
        if (state.debuggingCanvasCtx) {
          state.debuggingCanvasCtx.drawImage(
            videoElement,
            0,
            0,
            state.debuggingCanvasCtx.canvas.width,
            state.debuggingCanvasCtx.canvas.height
          );
          state.collectedEyesPatches.forEach(({ left, right }) => {
            [[left, 'green'], [right, 'blue']].forEach(([{ min, max }, color]) => {
              const width = max.x - min.x;
              const height = max.y - min.y;
              state.debuggingCanvasCtx.lineWidth = 2;
              state.debuggingCanvasCtx.strokeStyle = color;
              state.debuggingCanvasCtx.strokeRect(min.x, min.y, width, height);
            });
          })
          if (state.lastCapturedEyes) {
            const { left, right } = state.lastCapturedEyes;
            [left, right].forEach(({ min, max }) => {
              const width = max.x - min.x;
              const height = max.y - min.y;
              state.debuggingCanvasCtx.lineWidth = 2;
              state.debuggingCanvasCtx.strokeStyle = 'red';
              state.debuggingCanvasCtx.strokeRect(min.x, min.y, width, height);
            });
          }
        }
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
            min.x = min.x && min.x < x ? min.x : x;
            min.y = min.y && min.y < y ? min.y : y;
            max.x = max.x && max.x > x ? max.x : x;
            max.y = max.y && max.y > y ? max.y : y;
          })
          return { min, max }
        })

        state.lastCapturedEyes = { left: leftBBox, right: rightBBox };

        if (state.useNextFrameAsValidPosition) {
          state.collectedEyesPatches.push({
            left: leftBBox,
            right: rightBBox,
          });
          state.useNextFrameAsValidPosition = false;
        }

        // TODO: Detectar movimiento
        //       Movimientos laterales, up/down, alejación, acercación
        if (state.calibrationInProgress || state.detectionInProgress) {
          window.requestAnimationFrame(detectorLoop)
        }
      }
      Object.assign(module, {
        visualizeAt(canvasElement) {
          if (canvasElement?.nodeName !== "CANVAS") {
            throw new Error(
              `'movementDetector.visualizeAt' espera un elemento HTML de tipo 'canvas'.`
            )
          }
          canvasElement.width = videoElement.videoWidth
          canvasElement.height = videoElement.videoHeight
          state.debuggingCanvasCtx = canvasElement.getContext("2d")
        },
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
            state.collectedEyesPatches = []
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
          state.collectedEyesPatches = [];
          state.lastCapturedEyes = null;
          if (state.debuggingCanvasCtx) {
            state.debuggingCanvasCtx.clearRect(
              0,
              0,
              state.debuggingCanvasCtx.canvas.width,
              state.debuggingCanvasCtx.canvas.height
            )
          }
        },
      })
      document.dispatchEvent(new Event('movement-detector:ready'))
    })
  })

  return module
})()
