let runsCount = 5

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

document.addEventListener('movement-detector:ready', () => {
  const movementReporter = new MovementReporter();
  jsPsych.init({
    timeline: [{
      type: 'webgazer-init-camera',
    }, {
      type: 'fullscreen',
    }, {
      type: 'check-requirements',
    }, {
      type: 'calibrate-eye-tracker',
    }, {
      type: 'html-keyboard-response',
      stimulus: `
        <h2>Instrucciones</h2>
        <p>
          Vamos a realizar un experimento de antisacadas. <br>
          Se te mostrarán ${runsCount} iteraciones de tareas en las cuales un
          primer estímulo te indicará en qué dirección mirar respecto de un
          segundo estímulo. Si el primer estímulo es <span style="color: red;
          font-weight: bold;">rojo</span> tenés que mirar en la <span
          style="color: red; font-weight: bold;">dirección opuesta</span>. Si
          en cambio es <span style="color: green; font-weight:
          bold;">verde</span> tenés que mirar en la <span style="color: green;
          font-weight: bold;">misma dirección</span>. <br>
          Presioná cualquier tecla para comenzar.
        <p>
      `,
    }, {
      timeline: [{
        timeline: [{
          type: 'antisaccades',
        }, {
          on_start: function() {
            movementReporter.startNewWindow();
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
          conditional_function: function () {
            return movementReporter.detectedMovementSinceLastCheckpoint();
          },
        }],
        loop_function: function() {
          runsCount--;
          return runsCount > 0;
        },
      }]
    }],
    on_finish: function() {
      movementDetector.stop()
      jsPsych.data.get().localSave('json','antisaccades-experiment.json');
    },
    extensions: [
      {type: 'webgazer'}
    ]
  });
})
