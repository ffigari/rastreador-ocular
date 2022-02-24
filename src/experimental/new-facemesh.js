import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-cpu';
import * as faceLandmarksDetection from '@tensorflow-models/face-landmarks-detection';
import * as tfjsWasm from '@tensorflow/tfjs-backend-wasm';
import * as tf from '@tensorflow/tfjs-core';

import { setUpInputVideo } from './utils.js';

const paintEyesBBoxes = async (videoCanvasElement, videoElement) => {
  await tf.ready;
  console.log('tf versions:', tf.version_core)
  const model = await faceLandmarksDetection.load(
    faceLandmarksDetection.SupportedPackages.mediapipeFacemesh,
    { maxFaces: 1 }
  );
  console.log('current tf backend:', tf.getBackend());

  const ctx = videoCanvasElement.getContext('2d');
  const loop = async () => {
    const predictions = await model.estimateFaces({
      input: videoElement,
      returnTensors: false,
      flipHorizontal: false,
      predictIrises: false,
    });
    ctx.drawImage(
      videoElement, 0, 0,
      videoCanvasElement.width,
      videoCanvasElement.height
    );
    if (predictions.length > 0) {
      const { scaledMesh } = predictions[0];

      // TODO: The election of these coordinates strongly impact on the shape of
      //       the resulting bounding box. WG behavior should be imitated.
      const topLeftOrigin = {
        x: Math.round(scaledMesh[46][0]),
        y: Math.round(scaledMesh[46][1]),
      };
      const botRightOrigin = {
        x: Math.round(scaledMesh[128][0]),
        y: Math.round(scaledMesh[128][1]),
      };
      const left = {
        origin: topLeftOrigin,
        width: botRightOrigin.x - topLeftOrigin.x,
        height: botRightOrigin.y - topLeftOrigin.y,
      }

      ctx.globalAlpha = 0.4;
      ctx.fillStyle = 'red';
      ctx.fillRect(left.origin.x, left.origin.y, left.width, left.height);
      //ctx.fillRect(right.origin.x, right.origin.y, right.width, right.height);
      ctx.globalAlpha = 1;
    }
    window.requestAnimationFrame(loop);
  }
  window.requestAnimationFrame(loop);
};

document.addEventListener('DOMContentLoaded', async () => {
  const { videoCanvasElement, videoElement } = await setUpInputVideo();
  await paintEyesBBoxes(videoCanvasElement, videoElement);
});
