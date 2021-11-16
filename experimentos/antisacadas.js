let runsCount = 5

// TODO: Crear un módulo 'rastoc-lib' para meter todo el código que vaya a ser
//       provisto que no sea el rastreador en sí
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

document.addEventListener('movement-detector:ready', () => {
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
      timeline: convertToTrackedTimeline([{
        type: 'antisaccades',
      }]),
      loop_function: function() {
        runsCount--;
        return runsCount > 0;
      },
    }, {
      type: 'rastoc-finish'
    }],
    on_finish: function() {
      jsPsych.data.get().localSave('json','antisaccades-experiment.json');
    },
    extensions: [
      {type: 'webgazer'}
    ]
  });
})
