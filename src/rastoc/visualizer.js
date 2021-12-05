import { canvasDrawer, Loop } from '../utils.js';

let visualizer;
export const instantiateVisualizerWith = (estimator) => {
  if (!visualizer) {
    let gazeMarker;
    const gazeEstimatorUpdater = new Loop(() => {
      const p = estimator.lastPrediction;
      if (!p) {
        canvasDrawer.hidePoint(gazeMarker);
      } else {
        canvasDrawer.showPoint(gazeMarker);
        const [x, y] = p;
        canvasDrawer.moveToPixels(gazeMarker, x, y);
      }
    });
    visualizer = {
      showGazeEstimation() {
        gazeMarker = canvasDrawer.appendMarkerFor.gaze();
        canvasDrawer.hidePoint(gazeMarker);
        gazeEstimatorUpdater.turn.on();
      },
      hideGazeEstimation() {
        gazeEstimatorUpdater.turn.off();
        canvasDrawer.erasePoint(gazeMarker);
      },
    };
  }
  return visualizer;
}
