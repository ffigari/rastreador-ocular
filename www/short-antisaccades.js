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
      // This is computed following a logic similar to the one used to show the
      // side to side calibration points
      const step = Math.round((1 / 7) * (window.innerWidth / 2))
      cueXDistance = (cueGoesLeft ? 1 : -1) * 4 * step;
      return cueXDistance;
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
    timeline: [rastocJSPsych.createCalibrationBarrierNode("side-to-side"), {
      on_start() {
        startTs = new Date;
      },
      type: jsPsychPsychophysics,
      stimuli: [
        fixationMarker, visualCue,
      ],
      response_ends_trial: false,
      trial_duration:
        intraTrialBlankDuration + fixationDuration + interTrialBlankDuration + cueDuration,
      extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
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

const TRAINING_TRIALS_COUNT = 10;
const REAL_TRIALS_COUNT_PER_BLOCK = [50, 50, 50];

const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('json','short-antisaccades.json');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

jsPsych.run([
  {
    type: rastocJSPsych.EventsTrackingStart,
  },
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="text-align: left;">
      <p>
        Bienvenido a esta primera instancia de experimentación, gracias por
        participar c:
      </p>
      <p>
        En este experimento vas a realizar la tarea de antisacadas. Va a tomar
        aproximadamente 10 minutos. Es entonces importante que <b>te sientes
        cómodx</b>. Si estás con una notebook sentate tal que puedas estar en
        la misma posición durante unos minutos. 
      </p>
    </div>
    `,
    on_finish: function(data) {
      data.user_agent = navigator.userAgent;
      data.inner_width = window.innerWidth;
      data.inner_height = window.innerHeight;
    },
    choices: ["Continuar"],
  }, {
    type: jsPsychSurveyHtmlForm,
    button_label: 'Continuar',
    html: `
    <div style="text-align: left;">
      <p>
        Completá este par de datos tuyos.
      </p>

      <ul>
        <li>
          Edad? <br>
          <input name="edad" type="number" max="200" min="0" value="25">
        </li>

        <li>
          Vas a estar usando anteojos ahora durante el experimento? <br>

          <label for="no-anteojos-input">No</label>
          <input
            type="radio"
            name="anteojos"
            id="no-anteojos-input"
            value="no"
            checked
          >
          &nbsp;

          <label for="anteojos-input">Sí</label>
          <input
            type="radio"
            name="anteojos"
            id="anteojos-input"
            value="si"
          >
          &nbsp;

          <label for="lentes-de-contacto-input">Voy a usar lentes de contacto</label>
          <input
            type="radio"
            name="anteojos"
            id="lentes-de-contacto-input"
            value="contacto"
          >
        </li>
        <li>
          Qué datos de hardware sabés de tu compu? Este campo es informal y
          opcional pero cualquier dato sirve (cuánto RAM tenés? tenés placa de
          video externa? qué CPU?) <br>

          <input
            type="text"
            name="hardware"
            id="hardware-input"
          >
        </li>
      </ul>

      <p>
        Te aclaramos también que si bien vamos a usar la webcam, no vamos a
        estar guardando nada de lo grabado. El video lo usamos en vivo
        mientras realizás el experimento para estimar la coordenada de la
        pantalla que estás mirando. Al final del experimento a nosotros
        investigadores nos van a llegar únicamente estos datos que
        completaste arriba y una lista de esas coordenadas.
      </p>
    </div>
    `,
  }, {
    type: jsPsychWebgazerInitCamera,
    instructions: `
    <div style="text-align: left;">
      <p>
        Corregí la posición de la webcam para que tus ojos queden
        correctamente enfocados. Tu cabeza debería quedar en el centro del
        recuadro que aparece acá arriba.
      </p>
      <p>
        Cuando el recuadro se pinte de verde podés hacer click en
        "Continuar".
      </p>
    </div>
    `,
    button_text: "Continuar"
  }, {
    type: jsPsychFullscreen,
    message: `
    <div style="text-align: left;">
      <p>
        Para evitar distracciones te pedimos también que en la medida de lo
        posible durante la duración del experimento cierres aplicaciones que
        generen notificaciones y pongas el teléfono en modo no molestar.
        <br>
        Además vamos a cambiar a pantalla completa.
      </p>
      <p>
        En el próximo paso veremos el tema de la calibración.
      </p>
    </div>`,
    button_label: "Continuar"
  }, {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="text-align: left">
      <h3>Calibración</h3>
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
        en la pantalla.
        <br>
        Cada vez que aparezca uno tenés que
      </p>
      <ol>
        <li>fijar la mirada en él</li>
        <li>presionar la <b>barra de espacio</b></li>
      </ol>
      <p>
        En el próximo paso realizarás la calibración inicial.
        <br>
        Si más adelante detectamos demasiado movimiento entoces te vamos a
        avisar así recalibramos el sistema.
      </p>
    </div>
    `,
    choices: ["Continuar"],
  },
  rastocJSPsych.createEnsuredCalibrationNode("side-to-side"),
].concat(
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <div style="text-align: left">
          <p>
            Ahora vamos a hacer una ronda corta de la tarea de antisacadas para
            que te familiarices con ella. Luego haremos 150 repeticiones
            divididas en tres bloques con pausas entremedio.
          </p>
          <p>
            La tarea consiste en primero fijar la mirada en una
            <b>cruz central negra</b> y luego mirar en la <span style="color:
            red; font-weight: bold;">dirección opuesta</span> en la cual
            aparece un <span style="color: red; font-weight: bold;">círculo
            rojo lateral</span>.
          </p>
          <p>
            Al hacer click en "Continuar" realizarás 10 repeticiones de prueba 
            de la tarea.
          </p>
        </div>
        `,
    choices: ["Continuar"],
  },
  generateNAntisaccadeNodes(TRAINING_TRIALS_COUNT, idsGenerator)
).concat(
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
      <p>
        Ahora arrancan las repeticiones reales de la tarea. Acordate que tenés
        que mirar en la dirección <span style="color: red; font-weight:
        bold;">opuesta</span>. Presioná "Continuar" para arrancar.
      </p>
    `,
    choices: ["Continuar"]
  },
  generateNAntisaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[0], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
      <p>
        Fin del primer bloque. Descansá los ojos y cuando estés listx
        continuamos con el segundo bloque.
      </p>
    `,
    choices: ["Continuar"]
  },
  generateNAntisaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[1], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
      <p>
        Ya casi! Queda el último bloque. Luego de este bloque, cuando la
        pantalla quede en blanco habremos terminado y ahí ya podés cerrar esta
        pestaña. Gracias nuevamente por haber participado!
      </p>
    `,
    choices: ["Continuar"]
  },
  generateNAntisaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[2], idsGenerator)
).concat(
  {
    type: rastocJSPsych.EventsTrackingStop,
  },
));
