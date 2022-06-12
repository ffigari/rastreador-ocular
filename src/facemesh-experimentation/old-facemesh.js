import * as wgTf from 'wg-tfjs';
import { load as wgFacemeshLoader } from 'wg-tf-facemesh';

import { setUpInputVideo } from './utils.js';

const paintEyesBBoxes = async (videoCanvasElement, videoElement) => {
  await wgTf.ready;
  console.log('wgTf versions:', wgTf.version)
  const facemeshModel = await wgFacemeshLoader({"maxFaces": 1});
  console.log('current wgTf backend:', wgTf.getBackend())

  let right, left;
  let i = 0;
  const loop = async () => {
    console.log(`${i++}-th iteration of old predictor`);
    const ctx = videoCanvasElement.getContext('2d');
    ctx.drawImage(
      videoElement, 0, 0,
      videoCanvasElement.width,
      videoCanvasElement.height
    );
    if (left && right) {
      ctx.globalAlpha = 0.4;
      ctx.fillStyle = 'red';
      ctx.fillRect(left.origin.x, left.origin.y, left.width, left.height);
      ctx.fillRect(right.origin.x, right.origin.y, right.width, right.height);
      ctx.globalAlpha = 1;
    }
    const predictions = await facemeshModel.estimateFaces(videoCanvasElement);
    if (predictions.length > 0) {
      const { scaledMesh } = predictions[0];

      const leftOriginX = Math.round(Math.min(scaledMesh[247][0], scaledMesh[130][0], scaledMesh[25][0]));
      const leftOriginY = Math.round(Math.min(scaledMesh[247][1], scaledMesh[27][1], scaledMesh[190][1]));
      left = {
        origin: { x: leftOriginX, y: leftOriginY },
        width: Math.round(Math.max(scaledMesh[190][0], scaledMesh[243][0], scaledMesh[233][0]) - leftOriginX),
        height: Math.round(Math.max(scaledMesh[25][1], scaledMesh[23][1], scaledMesh[112][1]) - leftOriginY),
      }

      const rightOriginX = Math.round(Math.min(scaledMesh[414][0], scaledMesh[463][0], scaledMesh[453][0]));
      const rightOriginY = Math.round(Math.min(scaledMesh[414][1], scaledMesh[257][1], scaledMesh[467][1]));
      right = {
        origin: { x: rightOriginX, y: rightOriginY },
        width: Math.round(Math.max(scaledMesh[467][0], scaledMesh[359][0], scaledMesh[255][0]) - rightOriginX),
        height: Math.round(Math.max(scaledMesh[341][1], scaledMesh[253][1], scaledMesh[255][1]) - rightOriginY),
      }
    }
    window.requestAnimationFrame(loop);
  }
  window.requestAnimationFrame(loop);
};

document.addEventListener('DOMContentLoaded', async () => {
  const { videoCanvasElement, videoElement } = await setUpInputVideo();
  await paintEyesBBoxes(videoCanvasElement, videoElement);
});
