export default {
  name: 'rastoc-finish',
  trialCb: async function(display_element, trial) {
    rastoc.finish();
    jsPsych.finishTrial();
  }
}
