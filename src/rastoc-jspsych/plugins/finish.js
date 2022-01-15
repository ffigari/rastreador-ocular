export default {
  name: 'rastoc-finish',
  trialCb: async function(display_element, trial) {
    const events = rastoc.finish();
    jsPsych.finishTrial({
      rastocCategory: 'events',
      events
    });
  }
}
