export default {
  name: 'rastoc-finish',
  trialCb: async function(display_element, trial) {
    // TODO: Acá tendría que hacer `rastoc.finish()` luego de unificar los
    //       distintos módulos en uno sólo
    movementDetector.stop();
    jsPsych.finishTrial();
  }
}
