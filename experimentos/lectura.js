// https://stackoverflow.com/a/6274381/2923526
const shuffle = (a) => {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const totalRuns = 5;
let runsCount = totalRuns;

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
        Leete el texto que te aparezca y cuando esté bien leido presioná la
        barra de espacio.
      <p>
    `,
    }, {
      timeline: convertToTrackedTimeline([{
        type: 'html-keyboard-response',
        stimulus: function() {
          const baseString = "El patito nadaba en el estanque buscando pancitos flotantes.";
          if (runsCount === totalRuns) {
            return baseString;
          }
          return shuffle(baseString.split(" ")).join(" ");
        },
      }]),
      loop_function: function() {
        runsCount--;
        return runsCount > 0;
      },
    }, {
      type: 'rastoc-finish'
    }],
    on_finish: function() {
      jsPsych.data.get().localSave('json','lectura.json');
    },
    extensions: [
      {type: 'webgazer'}
    ]
  });
})

