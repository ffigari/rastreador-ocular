import { canvasDrawer, displayHTML } from '../../utils.js';

export default {
  name: 'ensure-calibrated-system',
  trialCb: async function(display_element, trial) {
    let calibrationEvents = [];
    if (rastoc.calibrationIsNeeded()) {
      const calibrator = await rastoc.switchTo.calibrating()

      // TODO: Por alguna razón este texto no se está mostrando
      await displayHTML(`
          <h2> Calibración </h2>
          <p>
            Te vamos a mostrar una serie de estímulos. A medida que aparezcan
            tenés que mirarlos y presionar la barra de espacio para indicar que
            los estás mirando. <br>
            Para comenzar presioná cualquier tecla.
          </p>
        `).at(display_element).untilAnyKeyIsPressed()

      calibrationEvents = await calibrator.runExplicitCalibration()

      rastoc.switchTo.idle()
    }
    jsPsych.finishTrial({
      rastocCategory: 'calibration',
      events: calibrationEvents,
    });
  }
}
