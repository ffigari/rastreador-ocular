const getRandomIntInclusive = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const getRandomBoolean = () => {
  return Math.random() < 0.5;
}
const idsGenerator = (function* () {
  let id = 0;
  while (true) {
    yield id++;
  }
})();
const getNValuesFrom = (
  n, gen
) => [...Array(n).keys()].map(() => gen.next().value);

const generateSaccadeNode = (trialId, isAntisaccade) => {
  const foreperiodDuration = getRandomIntInclusive(500, 1000);
  const fixationDuration = getRandomIntInclusive(500, 1000);
  // Para el RSI tendría sentido hacer una binormal porque en verdad importa
  // estar por arriba o por debajo del valor ese de 200 ms que menciona el 
  // artículo
  const rsiDuration = getRandomIntInclusive(150, 250); 
  const cueDuration = 700;

  const fixationMarker = {
    obj_type: 'cross',
    origin_center: true,
    startX: 0,
    startY: 0,
    show_start_time: foreperiodDuration,
    show_end_time: foreperiodDuration + fixationDuration,
    line_length: 40,
  };
  const cueGoesLeft = getRandomBoolean();
  const color = isAntisaccade ? 'red' : 'green';
  const visualCue = {
    obj_type: 'circle',
    origin_center: true,
    startX: (cueGoesLeft ? 1 : -1) * window.innerWidth / 4,
    startY: 0,
    show_start_time: foreperiodDuration + fixationDuration + rsiDuration,
    show_end_time:
    foreperiodDuration + fixationDuration + rsiDuration + cueDuration,
    radius: 20,
    line_color: color,
    fill_color: color,
  };

  // TODO: Registrar los timestamps de este trial y su id
  //       No encontré manera de capturar con precisión cuando empieza el
  //       trial de psychophysics. Se puede usar el on_start de jspsych y
  //       sumar las duraciones pero da una pequeña diferencia de 5 - 10 ms.
  return {
    timeline: [{
      type: 'ensure-calibrated-system',
    }, {
      type: "psychophysics",
      stimuli: [
        fixationMarker, visualCue,
      ],
      response_ends_trial: false,
      trial_duration:
      foreperiodDuration + fixationDuration + rsiDuration + cueDuration,
    }]
  };
}

const generateNSaccadeNodes = (
  n, gen, isAntisaccade
) => getNValuesFrom(n, gen).map((
  trialId
) => generateSaccadeNode(trialId, isAntisaccade));

const generateNProsaccadeNodes = (
  n, gen
) => generateNSaccadeNodes(n, gen, false);

const generateNAntisaccadeNodes = (
  n, gen
) => generateNSaccadeNodes(n, gen, true);

// TODO: Agregar algún comentario que explique en qué consiste la calibración
//       Dsp de explicar hacer la calibración inicial para darla de práctica
document.addEventListener('rastoc:ready', () => {
  jsPsych.init({
    timeline: [
      {
        type: 'html-keyboard-response',
        stimulus: `
        <p>
          Bienvenido a esta primera instancia de experimentación, gracias por
          participar c:
        </p>
        <p>
          En esta sesión vamos a realizar dos experimentos durante los cuales
          estaremos estimando qué punto de la pantalla estás mirando.  Cada uno
          tiene una duración de aproximadamente 10 minutos y ocurre además que
          nuestro sistema de estimación de mirada es muy vulnerable a
          movimientos de cabeza. Es entonces importante que <b>te sientes en un
          lugar cómodo</b> y posiciones la notebook tal que puedas estar en la
          misma posición durante unos minutos.
        </p>
        <p>
          El sistema en cuestión requiere ser inicialmente calibrado para poder
          estimar la mirada. Además, si luego detectamos demasiado movimiento
          procederemos a recalibrar. Tené en cuenta que <b>rotar la cabeza
          también cuenta como movimiento</b>. Idealmente durante los
          experimentos tendrías que estar <b>moviendo únicamente tus ojos</b>.
        </p>
        <p>
          Si te parece bien presioná cualquier tecla para arrancar la sesión.
        </p>
      `
      }, {
        type: 'webgazer-init-camera',
        instructions: `
          <p>
            Corregí la posición de la webcam para que tus ojos queden
            correctamente enfocados. Tu cabeza debería quedar en el centro del
            recuadro que aparece acá arriba.
          </p>
          <p>
            Cuando el recuadro se pinte de verde podés hacer click en
            "Continuar".
          </p>
        `,
        button_text: "Continuar"
      }, {
        type: 'rastoc-initialize',
        on_finish() {
          rastoc.visualizer.showGazeEstimation();
        },
      }, {
        type: "fullscreen",
        message: `
        <p>
          Para evitar distracciones te pedimos también que en la medida de lo
          posible durante la duración del experimento cierres aplicaciones que
          generen notificaciones y pongas el teléfono en modo no molestar.
        </p>
        <p>
          Además vamos a cambiar a pantalla completa.
        </p>
      `,
        button_label: "Continuar"
      }
    ].concat(
      {
        type: 'html-keyboard-response',
        stimulus: `
        <h2>1. Experimento de prosacadas</h2>
        <p>
          Esta tarea consiste en primero fijar la mirada en una <b>cruz central
          negra</b> y luego mirar un <span style="color: green; font-weight:
          bold;">círculo verde lateral</span>. La tarea toma ~3 segundos.
          Primero realizaremos 10 instancias para que te familiarices con ella
          y luego 250 instancias divididas en tres bloques. Entre cada bloque
          vas a tener oportunidad de descansar.
        </p>
        <p>
          Presioná cualquier tecla para comenzar.
        </p>
      `,
      },
      // TODO: Actualizar las cantidades de trials
      generateNProsaccadeNodes(5, idsGenerator),
      //{
      //  type: 'html-keyboard-response',
      //  stimulus: "Presioná cualquier tecla para arrancar con los bloques reales."
      //},
      //generateNProsaccadeNodes(10, idsGenerator),
      //{
      //  type: 'html-keyboard-response',
      //  stimulus: "Quedan 2 bloques, presioná cualquier tecla para continuar."
      //},
      //generateNProsaccadeNodes(10, idsGenerator),
      //{
      //  type: 'html-keyboard-response',
      //  stimulus: "Queda un último bloque de prosacadas, presioná cualquier tecla para continuar."
      //},
      //generateNProsaccadeNodes(10, idsGenerator)
    ).concat(
      {
        type: 'html-keyboard-response',
        stimulus: `
        <h2>2. Experimento de antisacadas</h2>
        <p>
          Ahora toca <b>evitar</b> mirar el círculo. La tarea comenzará ahora
          con la misma cruz central pero verás luego en cambio un <span
          style="color: red; font-weight: bold;">círculo rojo</span>. Cuando
          aparezca el círculo tendrás que mirar en la <span style="color: red;
          font-weight: bold;">dirección OPUESTA</span>.
        </p>
        <p>
          Presioná cualquier tecla para comenzar.
        </p>
      `,
      },
      // TODO: Actualizar las cantidades de trials
      generateNAntisaccadeNodes(5, idsGenerator),
      //{
      //  type: 'html-keyboard-response',
      //  stimulus: "Presioná cualquier tecla para arrancar con los bloques reales."
      //},
      //generateNAntisaccadeNodes(10, idsGenerator),
      //{
      //  type: 'html-keyboard-response',
      //  stimulus: "Quedan 2 bloques, presioná cualquier tecla para continuar."
      //},
      //generateNAntisaccadeNodes(10, idsGenerator),
      //{
      //  type: 'html-keyboard-response',
      //  stimulus: "Queda un último bloque, presioná cualquier tecla para continuar."
      //},
      //generateNAntisaccadeNodes(10, idsGenerator)
    ).concat({
      on_start() {
        rastoc.visualizer.hideGazeEstimation();
      },
      type: 'rastoc-finish'
    }),
    on_finish: function() {
      jsPsych.data.get().localSave('json','online-experiment.json');
    },
    extensions: [
      {type: 'webgazer'}
    ]
  })
});
