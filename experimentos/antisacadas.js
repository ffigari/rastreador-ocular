let runsCount = 5

document.addEventListener('movement-detector:ready', () => {
  document.addEventListener('movement-detector:movement:not-detected', () => {
    console.log('face ok')
  });
  document.addEventListener('movement-detector:movement:detected', () => {
    console.log('face movement detected')
  });
  document.addEventListener('movement-detector:calibration:reset', () => {
    console.log('face movement calibration reset')
  })
  jsPsych.init({
    timeline: [{
      type: 'webgazer-init-camera',
    }, {
      type: 'fullscreen',
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
        // TODO: Agregar para recalibrar condicionalmente
        //       Hay que ver cómo resetear WG
        //       Va a convenir agregar un plugin nuevo 'recalibrate-eyetracker'
        timeline: [{
          type: 'antisaccades',
        }, {
          timeline: [{
            type: 'html-keyboard-response',
            stimulus: function () {
              return `Detectamos una descalibración, vamos a recalibrar. Quedan ${runsCount - 1} iteraciones.`;
            },
          }, {
            type: 'html-keyboard-response',
            stimulus: 'recalibrando',
          }],
          conditional_function: function () {
            return (runsCount - 1) % 2 === 0;
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
