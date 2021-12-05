import plugins from './plugins/index.js'

plugins.forEach(({ name, trialCb }) => {
  jsPsych.plugins[name] = (function () {
    return {
      info: {
        name,
        parameters: {},
      },
      trial: trialCb
    }
  })();
})

window.convertToTrackedTimeline = (experiment, timeline) => {
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
      startedAt = new Date;
      const { visualizer } = await rastoc.switchTo.estimating();
      visualizer.showGazeEstimation();
    },

    timeline,

    on_timeline_finish() {
      const { visualizer } = rastoc.continueTo.estimate();
      visualizer.hideGazeEstimation();
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
