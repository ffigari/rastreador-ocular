import { Loop } from '../../utils.js';
import { create } from './eye-patches.js';
import {
  MINIMUM_CAMERA_WIDTH,
  MINIMUM_CAMERA_HEIGHT
} from '../../requirements-checker.js';

let movementDetector;
export const instantiateMovementDetector = async () => {
  if (movementDetector) {
    return movementDetector;
  }
  movementDetector = {};
  const state = {
    useNextFrameAsValidPosition: false,

    lastCapturedEyes: null,

    // Eye patches considered to be valid positions. They are collected during
    // the calibration phase and are then used to detect movements
    collectedEyesPatches: [],

    validEyesPosition: null,

    // Average distance of the last captured pair of eyes to the valid eyes
    // positions. Reported in pixels. Updated on each cycle while detection is
    // on.
    distanceToValidPosition: null,

    // Canvas element in which the movement detection should be debugged.
    // Captured video and estimated data will be drawn over it.
    debuggingCanvasCtx: null,
  };
  const _dispatch = (
    eventName
  ) => document.dispatchEvent(new Event(`rastoc_movement-detector:${eventName}`));
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

  if (document.readyState !== 'complete') {
    throw new Error(
      "The document should be fully loaded at this point. Be sure to encapsulate the call to this function inside a listener for the 'load' event."
    )
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
      const ctx = state.debuggingCanvasCtx
      if (!ctx) {
        throw new Error('el loop para dibujar necesita tener el canvas de debugging.')
      }
      return { ctx }
    });
    const calibrationLoop = new Loop(() => {
      if (state.useNextFrameAsValidPosition) {
        if (!state.lastCapturedEyes) {
          throw new Error(
            "No puede utilizarse el próximo frame como posición válida porque la última posición de los ojos es 'null'"
          );
        }
        state.collectedEyesPatches.push(state.lastCapturedEyes);
        state.validEyesPosition = create.validEyesPosition(state.collectedEyesPatches)
        state.useNextFrameAsValidPosition = false;
        dispatch.calibration.ready();
      }
    })
    const detectionLoop = new Loop(() => {
      if (state.lastCapturedEyes) {
        state.distanceToValidPosition =
          state.validEyesPosition.averageDistanceTo(state.lastCapturedEyes);
      }
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

    Object.assign(movementDetector, {
      debugFaceAt(canvasElement) {
        if (canvasElement?.nodeName !== "CANVAS") {
          throw new Error(
            `'movementDetector.debugFaceAt' espera un elemento HTML de tipo 'canvas'.`
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
      distanceToValidPosition() {
        return state.distanceToValidPosition;
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
        state.validEyesPosition = null;
        state.distanceToValidPosition = null;
        dispatch.calibration.reset();
      },
    });
    dispatch.moduleReady()
  })
  return movementDetector;
};
