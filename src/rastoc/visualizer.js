import { canvasDrawer } from '../utils.js';

let visualizer;
export const instantiateVisualizerWith = (estimator) => {
  if (!visualizer) {
    let gazeMarker;
    const handler = ({ detail: { x, y } }) => {
      canvasDrawer.showPoint(gazeMarker);
      canvasDrawer.moveToPixels(gazeMarker, x, y);
    }
    visualizer = {
      showGazeEstimation() {
        if (gazeMarker) {
          return;
        }
        gazeMarker = canvasDrawer.appendMarkerFor.gaze();
        canvasDrawer.hidePoint(gazeMarker);
        document.addEventListener('rastoc:gaze-estimated', handler)
      },
      hideGazeEstimation() {
        if (!gazeMarker) {
          return;
        }

        document.removeEventListener('rastoc:gaze-estimated', handler);
        canvasDrawer.erasePoint(gazeMarker);
        gazeMarker = undefined;
      },
    };
  }
  return visualizer;
}
