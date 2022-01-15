export default {
  name: 'ensure-calibrated-system',
  trialCb: async function(display_element, trial) {
    if (rastoc.calibrationIsNeeded()) {
      const calibrator = await rastoc.switchTo.calibrating();
      await calibrator.runExplicitCalibration();
      await rastoc.switchTo.estimating();
    }
    jsPsych.finishTrial();
  }
}
