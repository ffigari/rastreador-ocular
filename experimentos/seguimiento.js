let runsCount = 5

document.addEventListener('rastoc:ready', () => {
  jsPsych.init({
    timeline: [{
      type: 'webgazer-init-camera',
    }, {
      type: 'fullscreen',
    }, {
      type: 'rastoc-initialize',
    }, {
      type: 'html-keyboard-response',
      stimulus: `
        <h2>Instrucciones</h2>
        <p>
          Vamos a realizar un experimento de seguimiento. Se te va a mostrar un
          estímulo que tenés que seguir con la mirada.
        </p>
        <p>
          Presioná cualquier tecla para comenzar.
        </p>
      `,
    }, {
      timeline: convertToTrackedTimeline({
        name: 'seguimiento'
      }, [{
        type: 'seguimiento',
      }]),
      loop_function: function() {
        runsCount--;
        return runsCount > 0;
      },
    }, {
      type: 'rastoc-finish'
    }],
    on_finish: function() {
      jsPsych.data.get().localSave('json','seguimiento.json');
    },
    extensions: [
      {type: 'webgazer'}
    ]
  });
})
