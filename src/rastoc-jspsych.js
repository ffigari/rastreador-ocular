jsPsych.plugins['ensure-calibrated-system'] = (function(){
  return {
    info: {
      name: 'ensure-calibrated-system',
    },
    trial: async function(display_element, trial) {
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

        calibrationEvents = await calibrator.runExplicitCalibration(drawer)

        rastoc.switchTo.idle()
      }
      jsPsych.finishTrial({
        rastocCategory: 'calibration',
        events: calibrationEvents,
      });
    },
  }
})();

const convertToTrackedTimeline = (experiment, timeline) => {
  if (!experiment) {
    throw new Error(
      `Missing first parameter 'experiment' with experiment's info.`
    );
  }
  if (!timeline) {
    throw new Error(
      `Missing second parameter 'timeline' with experiment's jspsych timeline.`
    );
  }

  if (!experiment.name) {
    throw new Error(
      `First parameter 'experiment' is missing its 'name' property.`
    );
  }

  if (!Array.isArray(timeline)) {
    throw new Error(
      `Second parameter 'timeline' must be an array of JSPsych nodes.`
    );
  }

  let startedAt = null;

  return [{
      type: 'ensure-calibrated-system',
    }, {
    async on_timeline_start() {
      const estimator = await rastoc.switchTo.estimating()
      estimator.showVisualization()
      startedAt = new Date;
    },

    timeline,

    on_timeline_finish() {
      const estimator = rastoc.continueTo.estimate();
      estimator.hideVisualization();
      const events = rastoc.switchTo.idle();

      const {
        decalibrationWasDetectedSinceLastCalibration,
        decalibrationEvents,
      } = rastoc.checkDecalibration();
      if (decalibrationWasDetectedSinceLastCalibration) {
        events.push(...decalibrationEvents)
      }

      const lastTrialData = JSON.parse(jsPsych.data.getLastTrialData().json())[0];
      const givenConfig = lastTrialData?.trial?.config || null

      jsPsych.data.get().addToLast({
        rastocCategory: 'trial-instance',
        experiment,
        trial: {
          startedAt,
          endedAt: new Date,
          config: givenConfig,
        },
        events,
      });

    },
  }]
}
