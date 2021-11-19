let runsCount = 2

document.addEventListener('movement-detector:ready', () => {
  jsPsych.init({
    timeline: [{
      type: 'webgazer-init-camera',
    }, {
      type: 'fullscreen',
    }, {
      type: 'rastoc-initialize',
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
      timeline: convertToTrackedTimeline({
        name: 'antisacadas'
      }, [{
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
      jsPsych.data.get().localSave('json','antisacadas.json');
    },
    extensions: [
      {type: 'webgazer'}
    ]
  });
})
