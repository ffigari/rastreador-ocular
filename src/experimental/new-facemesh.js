import '@tensorflow/tfjs-backend-webgl';
import * as faceLandmarksDetection from '@tensorflow-models/face-landmarks-detection';
import * as tf from '@tensorflow/tfjs-core';

import { setUpInputVideo } from './utils.js';
import { Point, BBox } from '../types/index.js'

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

      [
        // left
        {
          eyeTopArcKeypoints: [
            25, 33, 246, 161, 160, 159, 158, 157, 173, 243,
          ],
          eyeBottomArcKeypoints: [
            25, 110, 24, 23, 22, 26, 112, 243,
          ],
        },
        // right
        {
          eyeTopArcKeypoints: [
            463, 398, 384, 385, 386, 387, 388, 466, 263, 255,
          ],
          eyeBottomArcKeypoints: [
            463, 341, 256, 252, 253, 254, 339, 255,
          ],
        },
      ].forEach(({ eyeTopArcKeypoints, eyeBottomArcKeypoints }) => {
        const topLeftOrigin = new Point(
          Math.round(Math.min(...eyeTopArcKeypoints.map(k => scaledMesh[k][0]))),
          Math.round(Math.min(...eyeTopArcKeypoints.map(k => scaledMesh[k][1])))
        );
        const bottomRightOrigin = new Point(
          Math.round(Math.max(...eyeBottomArcKeypoints.map(k => scaledMesh[k][0]))),
          Math.round(Math.max(...eyeBottomArcKeypoints.map(k => scaledMesh[k][1]))),
        );

        const eyeBBox = new BBox(
          topLeftOrigin,
          bottomRightOrigin.x - topLeftOrigin.x,
          bottomRightOrigin.y - topLeftOrigin.y,
        );

        ctx.globalAlpha = 0.4;
        ctx.fillStyle = 'red';
        ctx.fillRect(eyeBBox.origin.x, eyeBBox.origin.y, eyeBBox.width, eyeBBox.height);
        ctx.globalAlpha = 1;
      })

    }
    window.requestAnimationFrame(loop);
  }
  window.requestAnimationFrame(loop);
};

document.addEventListener('DOMContentLoaded', async () => {
  const { videoCanvasElement, videoElement } = await setUpInputVideo();
  await paintEyesBBoxes(videoCanvasElement, videoElement);
});
