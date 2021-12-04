import { canvasDrawer, forSingleSpaceBarOn, shuffle } from '../utils.js';

let calibrator;
export const instantiateCalibratorWith = (gazeEstimator, movementDetector) => {
  if (!calibrator) {
    const state = {
      atLeastOneCalibrationWasDone: false,
      systemIsCalibrated: false,
      lastDecalibrationEvents: [],
    };
    document.addEventListener('rastoc_movement-detector:movement:detected', () => {
      if (!state.systemIsCalibrated) {
        return;
      }
      Object.assign(state, {
        systemIsCalibrated: false,
        lastDecalibrationEvents: [
          { name: 'decalibration-detected', ts: new Date }
        ]
      })
    });
    calibrator = {
      calibrationIsNeeded() {
        return !state.systemIsCalibrated;
      },
      checkDecalibration() {
        return {
          decalibrationWasDetectedSinceLastCalibration: state.lastDecalibrationEvents.length > 0,
          decalibrationEvents: state.lastDecalibrationEvents,
        }
      },
      async reset() {
        if (!state.atLeastOneCalibrationWasDone) {
          return;
        }

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

        Object.assign(state, {
          atLeastOneCalibrationWasDone: true,
          systemIsCalibrated: true,
          lastDecalibrationEvents: [],
        })
        return calibrationEvents;
      }
    };
  }
  return calibrator;
};
