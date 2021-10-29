const movementDetector = (function() {
  const Loop = function (main, preMain) {
    let inProgress = false;
    const full = async () => {
      await main(preMain?.call() || {});
      if (inProgress) {
        go();
      }
    };

    let animationId = null;
    const go = () => {
      animationId = window.requestAnimationFrame(full);
    };
    return {
      get inProgress() {
        return inProgress;
      },
      turn: {
        on() {
          if (inProgress) {
            throw new Error('loop is already turned on.')
          }
          inProgress = true;
          go();
        },
        off() {
          if (!inProgress) {
            throw new Error('loop is already turned off.')
          }
          inProgress = false;
          animationId && window.cancelAnimationFrame(animationId);
          animationId = null;
        },
      },
    };
  };
  distance = (p1, p2) => Math.sqrt(
    Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2)
  )
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
        get corners() {
          return [
            { x: min.x, y: min.y },
            { x: min.x, y: max.y },
            { x: max.x, y: min.y },
            { x: max.x, y: max.y },
          ]
        }
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
        },
      };
    },
    validEyePosition: (patches) => {
      const axisCenter = (axis) => {
        return patches
          .map(({ center }) => center[axis])
          .reduce((acc, cur) => acc + cur, 0) / patches.length;
      };
      const center = {
        x: axisCenter('x'),
        y: axisCenter('y'),
      };
      const ratio = patches
        // Collect all corners
        .map(x => x.corners)
        // Flat them into a single array
        .reduce((acc, cur) => acc.concat(cur))
        // Compute each coord's distance to the center of all coordinates
        .map(p => distance(center, p))
        // Find the max distance
        .reduce((acc, cur) => acc > cur ? acc : cur)
        // Add 10% to the resulting value
        * 1.1;
      return {
        contains(eyePatch) {
          return eyePatch.corners.every(c => distance(center, c) <= ratio);
        },
        visualizeAt(ctx, color) {
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(center.x, center.y, 3, 0, Math.PI * 2);
          ctx.fill();

          ctx.globalAlpha = 0.3;
          ctx.beginPath();
          ctx.fillStyle = color;
          ctx.arc(center.x, center.y, ratio, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;
        },
      };
    },
    validEyesPosition: (eyesPatches) => {
      const [leftValidPosition, rightValidPosition] = eyesPatches.reduce((acc, cur) => {
        acc[0].push(cur.left);
        acc[1].push(cur.right);
        return acc;
      }, [[],[]]).map(x => create.validEyePosition(x))
      return {
        visualizeAt(ctx) {
          [[leftValidPosition, 'green'], [rightValidPosition, 'blue']].map(([
            eye, color
          ]) => eye.visualizeAt(ctx, color));
        },
        contains(eyesPair) {
          return leftValidPosition.contains(eyesPair.left)
            && rightValidPosition.contains(eyesPair.right)
        },
      };
    },
  }

  const module = {}
  const state = {
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
  };
  const _dispatch = (
    eventName
  ) => document.dispatchEvent(new Event(`movement-detector:${eventName}`));
  const dispatch = {
    moduleReady() {
      _dispatch('ready');
    },
    calibration: {
      ready() {
        _dispatch('calibration:ready');
      },
      reset() {
        _dispatch('calibration:reset')
      }
    },
    face: {
      notDetected() {
        _dispatch('face:not-detected');
      },
      detectedMultipleTimes() {
        _dispatch('face:detected-multiple-times');
      },
      detectedCorrectly() {
        _dispatch('face:detected-correctly');
      },
    },
    movement: {
      notDetected() {
        _dispatch('movement:not-detected');
      },
      detected() {
        _dispatch('movement:detected');
      },
    }
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
      const eyesCapturingLoop = new Loop(async () => {
        const predictions = await model.estimateFaces({
          input: videoElement
        })
        if (predictions.length === 0) {
          return dispatch.face.notDetected();
        }
        if (predictions.length > 1) {
          return dispatch.face.detectedMultipleTimes();
        }

        state.lastCapturedEyes = create.eyesPatchsPair(predictions[0]);
        return dispatch.face.detectedCorrectly();
      });
      const drawerLoop = new Loop(({
        ctx
      }) => {
        ctx.drawImage(videoElement, 0, 0, ctx.canvas.width, ctx.canvas.height);
        state.collectedEyesPatches.forEach((x) => x.visualizeAt(ctx, {
          leftColor: 'green',
          rightColor: 'blue',
        }));
        state.lastCapturedEyes?.visualizeAt(ctx, { color: 'red', })
        state.validEyesPosition?.visualizeAt(ctx)
      }, () => {
        ctx = state.debuggingCanvasCtx
        if (!ctx) {
          throw new Error('el loop para dibujar necesita tener el canvas de debugging.')
        }
        return { ctx }
      });
      const calibrationLoop = new Loop(() => {
        if (state.useNextFrameAsValidPosition) {
          state.collectedEyesPatches.push(state.lastCapturedEyes);
          state.validEyesPosition = create.validEyesPosition(state.collectedEyesPatches)
          state.useNextFrameAsValidPosition = false;
          dispatch.calibration.ready();
        }
      })
      const detectionLoop = new Loop(() => {
        if (
          state.lastCapturedEyes &&
          !state.validEyesPosition.contains(state.lastCapturedEyes)
        ) {
          return dispatch.movement.detected();
        }
        return dispatch.movement.notDetected();
      }, () => {
        if (!state.validEyesPosition) {
          throw new Error('No se definió la posición válida de los ojos.')
        }
      })

      eyesCapturingLoop.turn.on();

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
          drawerLoop.turn.on();
        },
        useNextFrameAsValidPosition() {
          if (!calibrationLoop.inProgress) {
            throw new Error(
              'Sólo se pueden agregar puntos durante la fase de calibración.'
            )
          }
          state.useNextFrameAsValidPosition = true;
        },
        start: {
          calibration() {
            state.collectedEyesPatches = []

            calibrationLoop.turn.on();
          },
          detection() {
            if (!state.validEyesPosition) {
              throw new Error(
                'No se puede pasar a detectar porque aún no se definió cuál es la posición válida de los ojos.'
              );
            }

            calibrationLoop.turn.off();
            detectionLoop.turn.on();
          }
        },
        stop() {
          calibrationLoop.inProgress && calibrationLoop.turn.off();
          detectionLoop.inProgress && detectionLoop.turn.off();

          state.collectedEyesPatches = [];
          state.lastCapturedEyes = null;
          state.validEyesPosition = null;
          dispatch.calibration.reset();
        },
        isReady: true,
      })
      dispatch.moduleReady()
    })
  })

  return module
})();
