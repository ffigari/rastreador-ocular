import { canvasDrawer, forSingleSpaceBarOn, shuffle } from '../utils.js';

// TODO: Si agregan eventos que asumen que este objeto es estatico entonces
//       de alguna manera hay que evitar que se puedan instanciar dos veces los
//       emisores de eventos
export const instantiateCalibratorWith = (gazeEstimator, movementDetector) => {
  return {
    async reset() {
      movementDetector.stop();

      await gazeEstimator.resetCalibration();
    },
    async runExplicitCalibration() {
      let stimulus = canvasDrawer.appendMarkerFor.calibration()
      const stimulusUpdater = (xPercentage, yPercentage) => {
        canvasDrawer.moveToPercentages(stimulus, xPercentage, yPercentage)
        return canvasDrawer.getCenterInPixels(stimulus)
      }
      let pixCoordinates = [
        [10,10], [10,50], [10,90],
        [50,10], [50,50], [50,90],
        [90,10], [90,50], [90,90],
      ]
      shuffle(pixCoordinates)
      movementDetector.start.calibration();
      let calibrationEvents = [
        { name: 'calibration-started', ts: new Date },
      ];
      for (const [xPerGroundTruth, yPerGroundTruth] of pixCoordinates) {
        // Draw this ground truth coordinate...
        const [
          xPixGT, yPixGT
        ] = stimulusUpdater(xPerGroundTruth, yPerGroundTruth);
        // ...and map the coordiante once the user presses the space bar
        await forSingleSpaceBarOn(document)
        movementDetector.useNextFrameAsValidPosition();
        calibrationEvents.push({
          name: 'calibration-stimulus-shown',
          ts: new Date,
          x: xPixGT,
          y: yPixGT,
        });
        gazeEstimator.calibratePoint(xPixGT, yPixGT);
      }
      calibrationEvents.push({ name: 'calibration-finished', ts: new Date });
      movementDetector.start.detection();
      canvasDrawer.erasePoint(stimulus)

      document.dispatchEvent(new Event('calibrator:system-calibrated'));
      return calibrationEvents;
    }
  }
};
