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
  const intraTrialBlankDuration = getRandomIntInclusive(500, 1000);
  const fixationDuration = getRandomIntInclusive(500, 1000);
  // Para el RSI tendría sentido hacer una binormal porque en verdad importa
  // estar por arriba o por debajo del valor ese de 200 ms que menciona el 
  // artículo
  const interTrialBlankDuration = getRandomIntInclusive(150, 250); 
  const cueDuration = 700;

  const fixationMarker = {
    obj_type: 'cross',
    origin_center: true,
    startX: 0,
    startY: 0,
    show_start_time: intraTrialBlankDuration,
    show_end_time: intraTrialBlankDuration + fixationDuration,
    line_length: 40,
  };
  const cueGoesLeft = getRandomBoolean();
  const color = isAntisaccade ? 'red' : 'green';
  const radius = 20;
  let cueXDistance;
  const visualCue = {
    obj_type: 'circle',
    origin_center: true,
    get startX() {
      const { px2deg } = jsPsych.data.get().values()
        .find((t) => t.trial_type === "virtual-chinrest")
      cueXDistance = Math.round(Math.min(
        (window.innerWidth / 2) - 2 * radius,
        10 * px2deg
      ));
      return (cueGoesLeft ? 1 : -1) * cueXDistance;
    },
    startY: 0,
    show_start_time:
      intraTrialBlankDuration + fixationDuration + interTrialBlankDuration,
    show_end_time:
      intraTrialBlankDuration + fixationDuration + interTrialBlankDuration + cueDuration,
    radius,
    line_color: color,
    fill_color: color,
  };

  let startTs;
  return {
    timeline: [{
      type: 'ensure-calibrated-system',
    }, {
      on_start() {
        startTs = new Date;
      },
      type: "psychophysics",
      stimuli: [
        fixationMarker, visualCue,
      ],
      response_ends_trial: false,
      trial_duration:
        intraTrialBlankDuration + fixationDuration + interTrialBlankDuration + cueDuration,
      on_finish(data) {
        const finishTs = new Date;
        data.rastocCategory = 'trial-instance';

        data.trialId = trialId;
        data.cueWasShownAtLeft = cueGoesLeft;
        data.experimentName = isAntisaccade ? 'antisaccade' : 'prosaccade';

        data.starTs = startTs.toISOString();
        data.finishTs = finishTs.toISOString();

        data.intraTrialBlankDuration = intraTrialBlankDuration;
        data.fixationDuration = fixationDuration;
        data.interTrialBlankDuration = interTrialBlankDuration;
        data.cueDuration = cueDuration;

        data.cueXDistance = cueXDistance;
      }
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

document.addEventListener('rastoc:ready', () => {
  jsPsych.init({
    timeline: [
      {
        type: 'html-button-response',
        stimulus: `
        <p>
          Bienvenido a esta primera instancia de experimentación, gracias por
          participar c:
        </p>
        <p>
          Nota: antes de mandar esto a los participantes hay que ajustar la
          cantidad de trials de cada bloque y sacar el punto rojo de debugging
          correspondiente a la mirada estimada.
        </p>
        <p>
          En esta sesión vamos a realizar dos tipos de tareas (prosacada y
          antisacada) en los cuales estaremos estimando qué punto de la
          pantalla estás mirando. En total toma unos 20 minutos  y ocurre
          además que nuestro sistema de estimación de mirada es muy vulnerable
          a movimientos de cabeza. Es entonces importante que <b>te sientes en
          un lugar cómodo</b> y posiciones la notebook tal que puedas estar en
          la misma posición durante unos minutos. De todos modos entre medio va
          a haber pausas para que puedas descansar un ratín.
        </p>
        <p>
          Además, para que podamos determinar el tamaño de tu pantalla vas a
          necesitar una tarjeta tipo SUBE, DNI o tarjeta de débito.
          <br>
          Cuanto tengas todo dale click a "Continuar" y arrancamos.
        </p>
      `,
        choices: ["Continuar"],
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
            <br>
            Además vamos a cambiar a pantalla completa.
          </p>
          <p>
            En el próximo paso estimaremos la dimensión de tu pantalla y luego
            veremos el tema de la calibración.
          </p>`,
        button_label: "Continuar"
      }, {
        type: 'virtual-chinrest',
        item_path: "card.png",
      }, {
        type: 'html-button-response',
        stimulus: `
          <p>
            El sistema en cuestión requiere ser inicialmente calibrado para
            poder estimar la mirada. Además, cada vez que detectemos demasiado
            movimiento procederemos a recalibrar. Tené en cuenta que <b>rotar
            la cabeza también cuenta como movimiento</b>. Idealmente durante
            los experimentos tendrías que estar <b>moviendo únicamente tus
            ojos</b>.
          </p>
          <p>
            La calibración consiste en fijar la mirada en <span style="color:
            blue; font-weight: bold;">círculos azules</span> que van a aparecer
            en la pantalla. Cada vez que aparezca uno tenés que fijar la mirada
            en él y presionar luego la <b>barra de espacio</b>.
          </p>
          <p>
            En el próximo paso relizarás la calibración inicial.
          </p>
        `,
        choices: ["Continuar"],
      },
      {
        type: 'ensure-calibrated-system',
      }
    ].concat(
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Vamos a arrancar con una ronda de prueba para que te familiarices
            con ambas tareas. Ahora tocan 10 repeticiones de cada una. Luego
            para cada tarea haremos 250 repeticiones divididas en tres bloques.
          </p>
          <p>
            La tarea de <span style="color: green; font-weight:
            bold;">prosacada</span> consiste en primero fijar la mirada en una
            <b>cruz central negra</b> y luego mirar en la <span style="color:
            green; font-weight: bold;">misma dirección</span> en la cual
            aparece un <span style="color: green; font-weight: bold;">círculo
            verde lateral</span>.
          </p>
          <p>
            Al hacer click en "Continuar" realizarás 10 repeticiones de prueba 
            de la tarea de <span style="color: green; font-weight:
            bold;">prosacada</span>.
          </p>
        `,
        choices: ["Continuar"],
      },
      generateNProsaccadeNodes(5, idsGenerator),
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Ahora vamos a practicar la tarea de <span style="color: red;
            font-weight: bold;">antisacada</span>. Similar a la tarea anterior,
            esta consiste en primero fijar la mirada en una <b>cruz central
            negra</b> pero en luego mirar en la <span style="color: red;
            font-weight: bold;">dirección opuesta</span> a la cual aparece un
            <span style="color: red; font-weight: bold;">círculo rojo
            lateral</span>.
          </p>
          <p>
            Al hacer click en "Continuar" realizarás 10 repeticiones de prueba 
            de la tarea de <span style="color: red; font-weight:
            bold;">antisacada</span>.
          </p>
      `,
        choices: ["Continuar"],
      },
      generateNAntisaccadeNodes(5, idsGenerator)
    )/*.concat(
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Ahora comenzaremos con los bloques reales, arrancando con uno de
            prosacadas (misma dirección).
          </p>
        `,
        choices: ["Continuar"]
      },
      generateNProsaccadeNodes(5, idsGenerator),
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Ahora toca el primer bloque de antisacadas (dirección opuesta).
          </p>
        `,
        choices: ["Continuar"]
      },
      generateNAntisaccadeNodes(5, idsGenerator),
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Segundo bloque de prosacada (misma dirección).
          </p>
        `,
        choices: ["Continuar"]
      },
      generateNProsaccadeNodes(5, idsGenerator),
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Segundo bloque de antisacada (dirección opuesta).
          </p>
        `,
        choices: ["Continuar"]
      },
      generateNAntisaccadeNodes(5, idsGenerator),
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Último bloque de prosacada (misma dirección).
          </p>
        `,
        choices: ["Continuar"]
      },
      generateNProsaccadeNodes(5, idsGenerator),
      {
        type: 'html-button-response',
        stimulus: `
          <p>
            Último bloque de antisacadas (dirección opuesta). Luego de este
            bloque, cuando la pantalla quede en blanco habremos terminado y ahí
            ya podés cerrar esta pestaña. Gracias nuevamente por haber
            participado!
          </p>
        `,
        choices: ["Continuar"]
      },
      generateNAntisaccadeNodes(5, idsGenerator)
    )*/.concat({
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
