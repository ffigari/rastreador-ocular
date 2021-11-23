const MovementReporter = function() {
  const resetMovementDetection = () => {
    movementDetected = false;
  }
  resetMovementDetection();

  document.addEventListener('movement-detector:movement:detected', () => {
    movementDetected = true;
  });
  document.addEventListener('movement-detector:calibration:reset', () => {
    resetMovementDetection();
  })

  Object.assign(this, {
    detectedMovementSinceLastCheckpoint: () => {
      return movementDetected;
    },
    startNewWindow() {
      resetMovementDetection();
    }
  })
}

// TODO: Renombrar módulo a 'rastoc-jspsych'

// TODO: Sacar la calibración de afuera y acá calibrar si no está calibrado o
//       si se detecto una descalibración
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
      `Second parameter 'timeline' is not an array as expected.`
    );
  }

  const movementReporter = new MovementReporter();

  let startedAt = null;

  return [{
    async on_timeline_start() {
      const estimator = await rastoc.switchTo.estimating()
      estimator.showVisualization()

      movementReporter.startNewWindow();
      startedAt = new Date;
    },

    timeline,

    on_timeline_finish() {
      const estimator = rastoc.continueTo.estimate();
      estimator.hideVisualization();
      const gazeEstimationEvents = rastoc.switchTo.idle();

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
        events: gazeEstimationEvents,
      });

    },
  }, {
    conditional_function: function () {
      return movementReporter.detectedMovementSinceLastCheckpoint();
    },
    timeline: [{
      type: 'html-keyboard-response',
      stimulus: function () {
        return `Detectamos una descalibración, vamos a recalibrar. Presioná cualquier tecla para continuar.`;
      },
      on_start() {
        // TODO: Acá hay que avisar esto segun el formato elegido
        jsPsych.data.get().addToLast({ decalibration_detected: true });
      },
    }, {
      // TODO: Replace this with single calibration plugin and push required
      //       data
      type: 'recalibrate-eye-tracker',
    }],
  }]
}
