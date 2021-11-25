// https://stackoverflow.com/a/6274381/2923526
const shuffle = (a) => {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const totalRuns = 3;
let runsCount = totalRuns;

let textStimulus = "El patito nadaba en el estanque buscando pancitos flotantes.";

document.addEventListener('movement-detector:ready', () => {
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
        Leete el texto que te aparezca y cuando esté bien leido presioná la
        barra de espacio.
      <p>
    `,
    }, {
      timeline: convertToTrackedTimeline({
        name: 'lectura',
      }, [{
        type: 'html-keyboard-response',
        stimulus: function() {
          if (runsCount < totalRuns) {
            textStimulus = shuffle(textStimulus.split(" ")).join(" ");
          }
          return textStimulus;
        },
        on_finish: function(data) {
          data.trial = {
            config: {
              shownText: textStimulus,
            }
          }
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

