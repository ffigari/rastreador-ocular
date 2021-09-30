const movementDetector = (function() {
  const create = {
    eyePatch: (prediction, keypointsIndexes) => {
      const min = { x: null, y: null }
      const max = { x: null, y: null };
      keypointsIndexes.forEach(keypointIndex => {
        const [x, y, z] = prediction.scaledMesh[keypointIndex];
        min.x = min.x && min.x < x ? min.x : x;
        min.y = min.y && min.y < y ? min.y : y;
        max.x = max.x && max.x > x ? max.x : x;
        max.y = max.y && max.y > y ? max.y : y;
      })
      return {
        min,
        max,
        width: max.x - min.x,
        height: max.y - min.y,
        center: {
          x: (min.x + max.x) / 2,
          y: (min.y + max.y) / 2,
        },
        visualizeAt(ctx, color) {
          ctx.lineWidth = 2;
          ctx.strokeStyle = color || 'black';
          ctx.strokeRect(this.min.x, this.min.y, this.width, this.height);
        },
      };
    },
    eyesPatchsPair: (prediction) => {
      // Los índices de los keypoints pueden consultarse en
      // https://github.com/tensorflow/tfjs-models/blob/master/face-landmarks-detection/mesh_map.jpg
      const [leftEyePatch, rightEyePatch] = [
        [189, 244, 232, 230, 228, 226, 225, 223, 221],
        [413, 464, 452, 450, 448, 446, 445, 443, 441],
      ].map(keypointsIndexes => create.eyePatch(prediction, keypointsIndexes))
      return {
        left: leftEyePatch,
        right: rightEyePatch,
        visualizeAt(ctx, { leftColor, rightColor, color }) {
          [
            [this.left,  leftColor  || color],
            [this.right, rightColor || color],
          ].map(([patch, color]) => patch.visualizeAt(ctx, color))
        }
      };
    },
    validEyePosition: (patches) => {
      const axisCenter = (axis) => {
        return patches
        .map(({ center }) => center[axis])
        .reduce((acc, cur) => acc + cur, 0) / patches.length;
      }
      const center = {
        x: axisCenter('x'),
        y: axisCenter('y'),
      }
      return {
        visualizeAt(ctx, color) {
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(center.x, center.y, 3, 0, Math.PI * 2);
          ctx.fill();
        },
      };
    },
    validEyesPosition: (eyesPatches) => {
      const [leftEye, rightEye] = eyesPatches.reduce((acc, cur) => {
        acc[0].push(cur.left);
        acc[1].push(cur.right);
        return acc;
      }, [[],[]]).map(x => create.validEyePosition(x))
      return {
        visualizeAt(ctx) {
          [[leftEye, 'green'], [rightEye, 'blue']].map(([
            eye, color
          ]) => eye.visualizeAt(ctx, color));
        }
      };
    },
  }

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

    validEyesPosition: null,

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
          state.collectedEyesPatches.forEach((x) => x.visualizeAt(
            state.debuggingCanvasCtx, { leftColor: 'green', rightColor: 'blue', }
          ));
          state.lastCapturedEyes?.visualizeAt(state.debuggingCanvasCtx, {
            color: 'red',
          })
          state.validEyesPosition?.visualizeAt(state.debuggingCanvasCtx)
        }
        const predictions = await model.estimateFaces({
          input: videoElement
        })
        // TODO: En lugar de tirar un error habría que informar al usuario con
        //       algún evento.
        if (predictions.length === 0) {
          throw new Error('No se detectó ninguna cara.')
        }
        if (predictions.length > 1) {
          throw new Error('Se detectó más de una cara.')
        }
        const eyesPatchsPair = create.eyesPatchsPair(predictions[0]);
        state.lastCapturedEyes = eyesPatchsPair;
        if (state.useNextFrameAsValidPosition) {
          state.collectedEyesPatches.push(eyesPatchsPair);
          state.validEyesPosition =
            create.validEyesPosition(state.collectedEyesPatches)
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
          state.validEyesPosition = null;
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
