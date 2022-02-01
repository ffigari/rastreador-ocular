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
      // TODO Add virtual chinrest support back
      // const { px2deg } = jsPsych.data.get().values()
      //   .find((t) => t.trial_type === "virtual-chinrest")
      // cueXDistance = Math.round(Math.min(
      //   (window.innerWidth / 2) - 2 * radius,
      //   10 * px2deg
      // ));
      cueXDistance = (window.innerWidth / 2) - 2 * radius;
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
    // TODO: Use side to side calibration
    timeline: [rastocJSPsych.createCalibrationBarrierNode(), {
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

        // TODO: Is it needed for this value to be translated into a coordinate?
        //       Storing the coordinates of the center of the viewport should be
        //       enough
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
const REAL_TRIALS_COUNT_PER_BLOCK = [50, 75, 75];

const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('json','antisaccades.json');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

jsPsych.run([
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="text-align: left;">
      <p>
        Bienvenido a esta primera instancia de experimentación, gracias por
        participar c:
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
        Además, para que podamos determinar el tamaño de tu pantalla <b>vas a
        necesitar una tarjeta tipo SUBE, DNI o tarjeta de débito</b>.
        <br>
        Cuanto tengas todo dale click a "Continuar" y arrancamos.
      </p>
    </div>
    `,
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

          <label for="lentes-de-contacto-input">Uso lentes de contacto</label>
          <input
            type="radio"
            name="anteojos"
            id="lentes-de-contacto-input"
            value="contacto"
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
        En el próximo paso estimaremos la dimensión de tu pantalla y luego
        veremos el tema de la calibración.
      </p>
    </div>`,
    button_label: "Continuar"
  }, /*{
    type: 'virtual-chinrest',
    item_path: "card.png",
    adjustment_prompt: `
    <div style="text-align: left;">
      <p>
        Apoya la tarjeta que elegiste antes contra la imagen de acá arriba.
        <br>
        Después clickeá y arrastrá la esquina inferior derecha de la imagen
        hasta que coincidan los tamaños.
      </p>
    <div>
    `,
    adjustment_button_prompt:
      "Clickeá acá cuando el tamaño de la imagen sea el correcto",
    blindspot_prompt: `
    <div style="text-align: left">
      <p>Ahora vamos a medir qué tan lejos de la pantalla estás.</p>
      <ol>
        <li>Poné tu mano izquierda sobre la <b>barra de espacio</b>.</li>
        <li>Cubrí tu ojo derecho con tu mano derecha.</li>
        <li>Usando tu ojo izquierdo, enfocá el cuadrado negro. Asegurate
        de mantener el foco en él.</li>
        <li>El <span style="color: red; font-weight: bold;">círculo
        rojo</span> va a desaparecer mientras se mueve desde la derecha a
        la izquierda. Presioná la barra de espacio cuando el círculo
        desaparezca.</li>
      </ol>
      <p>Presioná la barra de espacio cuando estés listo para comenzar.</p>
    </div>
      `,
    redo_measurement_button_label: "No, eso no parece correcto. Reintentar.",
    blindspot_done_prompt: "Sí, esa distancia parece bien.",
    blindspot_measurements_prompt: "Medidas restantes:",
    viewing_distance_report: `
      <p>
        Basado en tus respuestas, estás sentandote a aproximadamente <span
        id='distance-estimate' style='font-weight: bold;'></span> de la
        pantalla.
      </p>
      <p>
        Te parece que está bien esa estimación?
      </p>
    `
  },*/ {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="text-align: left">
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
        En el próximo paso relizarás la calibración inicial.
        <br>
        Si más adelante te vuelve a aparecer la pantalla en blanco con el
        punto azul entonces el sistema tiene que ser recalibrado. Cuando
        haya que recalibrar no van a volver a aparecer las intrucciones.
      </p>
    </div>
    `,
    choices: ["Continuar"],
  },
  // TODO: Replace free calibration with side to side calibration
  rastocJSPsych.createFreeCalibrationNode()
].concat(
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <div style="text-align: left">
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
        </div>
        `,
    choices: ["Continuar"],
  },
  generateNProsaccadeNodes(TRAINING_TRIALS_COUNT, idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <div style="text-align: left">
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
            Ahora comenzaremos con los bloques reales, arrancando con uno de
            prosacadas (mirar en la misma dirección).
          </p>
        `,
    choices: ["Continuar"]
  },
  generateNProsaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[0], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
          <p>
            Ahora toca el primer bloque de antisacadas (mirar en la dirección opuesta).
          </p>
        `,
    choices: ["Continuar"]
  },
  generateNAntisaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[0], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
          <p>
            Segundo bloque de prosacada (mirar en la misma dirección).
          </p>
        `,
    choices: ["Continuar"]
  },
  generateNProsaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[1], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
          <p>
            Segundo bloque de antisacada (mirar en la dirección opuesta).
          </p>
        `,
    choices: ["Continuar"]
  },
  generateNAntisaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[1], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
          <p>
            Último bloque de prosacada (mirar en la misma dirección).
          </p>
        `,
    choices: ["Continuar"]
  },
  generateNProsaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[2], idsGenerator),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
          <p>
            Último bloque de antisacadas (mirar en la dirección opuesta). Luego de este
            bloque, cuando la pantalla quede en blanco habremos terminado y ahí
            ya podés cerrar esta pestaña. Gracias nuevamente por haber
            participado!
          </p>
        `,
    choices: ["Continuar"]
  },
  generateNAntisaccadeNodes(REAL_TRIALS_COUNT_PER_BLOCK[2], idsGenerator)
));
