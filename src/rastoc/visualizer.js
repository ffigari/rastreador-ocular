import { canvasDrawer, Loop } from '../utils.js';

let visualizer;
export const instantiateVisualizerWith = (estimator) => {
  if (!visualizer) {
    let gazeMarker;
    let handlerId;
    visualizer = {
      showGazeEstimation() {
        gazeMarker = canvasDrawer.appendMarkerFor.gaze();
        canvasDrawer.hidePoint(gazeMarker);
        handlerId = document.addEventListener('rastoc:gaze-estimated', ({ detail: { x, y } }) => {
          canvasDrawer.showPoint(gazeMarker);
          canvasDrawer.moveToPixels(gazeMarker, x, y);
        })
      },
      hideGazeEstimation() {
        document.removeEventListener('rastoc:gaze-estimated', handlerId)
        canvasDrawer.erasePoint(gazeMarker);
      },
    };
  }
  return visualizer;
}
