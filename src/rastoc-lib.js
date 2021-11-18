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

// TODO: No recalibrar si la descalibración es en el último trial
//       Aunque eso implicaría que esta función sea consciente del loop así que
//       no sé muy bien cómo convenga resolverlo
const convertToTrackedTimeline = (timeline) => {
  const movementReporter = new MovementReporter();
  return [{
    type: 'start-estimation-window',
    on_start() {
      movementReporter.startNewWindow();
    }
  }, {

    timeline

  }, {
    type: 'finish-estimation-window',
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
        jsPsych.data.get().addToLast({ decalibration_detected: true });
      },
    }, {
      type: 'recalibrate-eye-tracker',
    }],
  }]
}
