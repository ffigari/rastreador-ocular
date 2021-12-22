import { canvasDrawer, forSingleSpaceBarOn, shuffle } from '../utils.js';

let calibrator;
export const instantiateCalibratorWith = (movementDetector) => {
  const wgExt = jsPsych.extensions.webgazer;
  if (!calibrator) {
    const state = {
      atLeastOneCalibrationWasDone: false,
      systemIsCalibrated: false,
    };
    document.addEventListener('rastoc_movement-detector:movement:detected', () => {
      if (!state.systemIsCalibrated) {
        return;
      }
      document.dispatchEvent(new CustomEvent('rastoc:decalibration', {
        detail: {
          name: 'decalibration-detected',
          ts: new Date,
        },
      }))
      Object.assign(state, {
        systemIsCalibrated: false,
      })
    });
    calibrator = {
      calibrationIsNeeded() {
        return !state.systemIsCalibrated;
      },
      async reset() {
        if (!state.atLeastOneCalibrationWasDone) {
          return;
        }

        movementDetector.stop();
        await wgExt.resetCalibration();
      },
      async runExplicitCalibration() {
        await wgExt.resume();
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
        document.dispatchEvent(new CustomEvent('rastoc:calibration', {
          detail: {
            name: 'calibration-started',
            ts: new Date,
          },
        }))
        for (const [xPerGroundTruth, yPerGroundTruth] of pixCoordinates) {
          // Draw this ground truth coordinate...
          const [
            xPixGT, yPixGT
          ] = stimulusUpdater(xPerGroundTruth, yPerGroundTruth);
          // ...and map the coordiante once the user presses the space bar
          await forSingleSpaceBarOn(document)
          movementDetector.useNextFrameAsValidPosition();
          document.dispatchEvent(new CustomEvent('rastoc:calibration', {
            detail: {
              name: 'calibration-stimulus-shown',
              ts: new Date,
              x: xPixGT,
              y: yPixGT,
            },
          }))
          wgExt.calibratePoint(xPixGT, yPixGT);
        }
        document.dispatchEvent(new CustomEvent('rastoc:calibration', {
          detail: {
            name: 'calibration-finished',
            ts: new Date,
          },
        }))
        movementDetector.start.detection();
        canvasDrawer.erasePoint(stimulus)

        Object.assign(state, {
          atLeastOneCalibrationWasDone: true,
          systemIsCalibrated: true,
        })
        await wgExt.pause();
      }
    };
  }
  return calibrator;
};
