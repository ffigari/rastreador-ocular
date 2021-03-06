const getRandomIntInclusive = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const getRandomBoolean = () => {
  return Math.random() < 0.5;
}

const displayMsg = (msg, ms) => {
  return {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: msg,
    choices: "NO_KEYS",
    trial_duration: ms,
  }
}

const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('csv', 'antisaccades.csv');
    location.href = "https://neuropruebas.org/";
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

const saccade = ({ anti, isTutorial }) => {
  const showVisualCueAtLeft = getRandomBoolean();
  const durations = {
    interTrial: 925,
    fixation: getRandomIntInclusive(900, 1500),
    intraTrial: 75,
    visualCue: 150,
    responseAwait: 650,
    get total() {
      return this.responseEnd;
    },
    get itiEnd() {
      return this.interTrial;
    },
    get fixEnd() {
      return this.itiEnd + this.fixation;
    },
    get intraEnd() {
      return this.fixEnd + this.intraTrial;
    },
    get visualEnd() {
      return this.intraEnd + this.visualCue;
    },
    get responseEnd() {
      return this.visualEnd + this.responseAwait;
    },
  }

  const fixationMarker = {
      obj_type: 'manual',
      drawFunc: (stim, canvas, ctx, elapsedTime, sumOfStep) => {
        // cx = canvas' center
        const cx = Math.round(canvas.width / 2);
        const cy = Math.round(canvas.height / 2);

        ctx.beginPath();
        ctx.lineWidth = 6;
        const size = 15
        if (anti) {
          ctx.moveTo(cx - size, cy - size);
          ctx.lineTo(cx + size, cy + size);
          ctx.moveTo(cx - size, cy + size);
          ctx.lineTo(cx + size, cy - size);
        } else {
          ctx.arc(cx, cy, size, 0, 2 * Math.PI, false);
        }
        ctx.stroke();
      }
  }
  const placeholder = {
    obj_type: 'rect',
    origin_center: true,
    line_color: 'black',
    width: 45,
    height: 45,
    startY: 0,
  }
  const visualCue = {
    obj_type: 'circle',
    origin_center: true,
    fill_color: 'black',
    radius: 20,
    startY: 0,
  }
  // This already coincides with the positions in which the calibration points
  // are shown but ideally the regions of interest should be abstracted somehow
  // so that these distances do not have to be redefined.
  // Check `interestRegionsXs` object at `src/rastoc-jspsych/index.js` for more
  // info.
  const delta = () => Math.round(2 * window.innerWidth / 6);
  return {
    type: jsPsychPsychophysics,
    background_color: '#d3d3d3',
    stimuli: [{
      show_start_time: durations.itiEnd,
      show_end_time: durations.fixEnd,
      ...fixationMarker
    }, {
      show_start_time: durations.intraEnd,
      show_end_time: durations.responseEnd,
      ...fixationMarker
    }, {
      // left placeholder
      show_start_time: durations.itiEnd,
      show_end_time: durations.fixEnd,
      ...placeholder,
      get startX() {
        return - delta();
      },
    }, {
      // left placeholder
      show_start_time: durations.intraEnd,
      show_end_time: durations.responseEnd,
      ...placeholder,
      get startX() {
        return - delta();
      },
    }, {
      // right placeholder
      show_start_time: durations.itiEnd,
      show_end_time: durations.fixEnd,
      ...placeholder,
      get startX() {
        return delta();
      },
    }, {
      // right placeholder
      show_start_time: durations.intraEnd,
      show_end_time: durations.responseEnd,
      ...placeholder,
      get startX() {
        return delta();
      },
    }, {
      show_start_time: durations.intraEnd,
      show_end_time: durations.visualEnd,
      ...visualCue,
      get startX() {
        return (showVisualCueAtLeft ? -1 : 1) * delta();
      },
    }],
    response_ends_trial: false,
    trial_duration: durations.total,
    extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
    on_finish(data) {
      data.isSaccadeExperiment = true;
      data.typeOfSaccade = anti ? 'antisaccade' : 'prosaccade';
      data.isTutorial = isTutorial;

      data.cueShownAtLeft = showVisualCueAtLeft;

      data.itiEnd = durations.itiEnd;
      data.fixEnd = durations.fixEnd;
      data.intraEnd = durations.intraEnd;
      data.visualEnd = durations.visualEnd;
      data.responseEnd = durations.responseEnd;

      // viewport dimensions to check if the size of the screen changed since
      // last calibration
      data.viewportWidth = window.innerWidth;
      data.viewportHeight = window.innerHeight;

      data.systemIsStillCalibrated = rastoc.isCorrectlyCalibrated;
    },
  }
};

const REPETITIONS_PER_BLOCK = 20;
const nSaccades = (options) => {
  options.n = options.n || REPETITIONS_PER_BLOCK;
  options.isTutorial = options.isTutorial === undefined
    ? false
    : options.isTutorial;

  let saccades = [];
  for (let i = 0; i < options.n; ++i) {
    saccades.push(saccade({
      anti: options.anti,
      isTutorial: options.isTutorial,
    }));
  }
  return saccades
};

const htmlCross  = `<span style="font-size:48px;"><b>&#10799;</b></span>`;
const htmlCircle = `<span style="font-size:28px;"><b>&#9711;</b></span>`;

const proReminder = `${htmlCircle} = mirar en la MISMA direcci??n`;
const antiReminder = `${htmlCross} = mirar en la direcci??n OPUESTA`;

const saccadesBlocksPair = (options) => {
  options = options || {};
  return {
    timeline: [
      rastocJSPsych.ensureCalibration({
        performValidation: true,
        forceCalibration: options.forceCalibration,
        maxRetries: 1,
      }),
      displayMsg(`
        <h3>Bloque de prosacada</h3>
        <p>${proReminder}<p>
        ${prosaccadeGifInstructions}
      `, 3000),
      ...nSaccades({ anti: false, n: options.n, isTutorial: options.isTutorial }),
      rastocJSPsych.ensureCalibration({
        performValidation: true,
        maxRetries: 1,
      }),
      displayMsg(`
        <h3>Bloque de antisacadas</h3>
        <p>${antiReminder}<p>
        ${antisaccadeGifInstructions}
      `, 3000),
      ...nSaccades({ anti: true, n: options.n, isTutorial: options.isTutorial }),
    ]
  }
}

const gifInstructionsCSS = `
  <style>
    .gif-instruction {
      border: 2px solid black;
      padding-right: 10px;
      padding-left: 10px;
      margin-bottom: 10px;
    }
    .gif-instruction > img {
      width: 70%;
      height: auto;
      display: block;
      margin-left: auto;
      margin-right: auto;
      border: 1px solid black;
    }
  </style>
`;
const prosaccadeGifInstructions = `
  ${gifInstructionsCSS}
  <div class="gif-instruction">
    <h4>Prosacada</h4>
    <img src="prosaccade.gif" alt="prosaccade instructions" /> 
    <p>Mirar hacia el mismo lado</p>
  </div>
`;
const antisaccadeGifInstructions = `
  ${gifInstructionsCSS}
  <div class="gif-instruction">
    <h4>Antisacada</h4>
    <img src="antisaccade.gif" alt="antisaccade instructions" /> 
    <p>Mirar hacia el lado contrario</p>
  </div>
`;

const tutorial = () => {
  let retry = false;
  const retryChoices = {
    html: `
      <div style="left: calc(50% - 400px); width:800px;">
        <p>
          Ah?? terminamos el tutorial. Quer??s hacerlo de vuelta?
        </p>
      </div>`,
    yes: "s??, quiero hacer nuevamente el tutorial",
    no: "no, ya qued?? claro",
    get choices() {
      return [this.yes, this.no];
    },
    check(r) {
      return this.yes === this.choices[r]
    },
  };
  return {
    timeline: [{
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <div style="left: calc(50% - 400px); width:800px;">
        <h2>Tutorial</h2>
        <p>
          A lo largo de este experimento vas a realizar muchas repeticiones de
          tareas de prosacadas y antisacadas. Cada una de estas repeticiones
          dura menos de tres segundos. En cada una va a aparecer un est??mulo
          central y luego uno lateral. Cada vez que aparezca el est??mulo
          central, fij?? la mirada en ??l hasta que desaparezca.
        </p>
      </div>`,
      choices: ["continuar"],
    }, {
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <div style="left: calc(50% - 400px); width:800px;">
        <h2>Tutorial</h2>
        <h3>Prosacadas</h3>
        <p>
          En la tarea de prosacada ten??s que mirar en la MISMA direcci??n en la 
          cual aparezca el est??mulo lateral. Cuando el est??mulo central sea un
          c??rculo (${htmlCircle}), estamos ante una tarea de prosacadas.
        </p>
        ${prosaccadeGifInstructions}
      </div>`,
      choices: ["continuar"],
    }, {
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <div style="left: calc(50% - 400px); width:800px;">
        <h2>Tutorial</h2>
        <h3>Antisacadas</h3>
        <p>
          En cambio, en la tarea de antisacadas ten??s que mirar en la direcci??n
          OPUESTA en la cual aparece el est??mulo lateral. Para estas tareas el
          est??mulo central va ser una cruz (${htmlCross}).
        </p>
        ${antisaccadeGifInstructions}
      </div>`,
      choices: ["continuar"],
    }, {
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <div style="left: calc(50% - 400px); width:800px;">
        <h2>Tutorial</h2>
        <h3>Calibraci??n y validaci??n</h3>
        <p>
          El sistema en cuesti??n requiere ser inicialmente calibrado para
          poder estimar la mirada. Adem??s, cada vez que detectemos demasiado
          movimiento procederemos a recalibrar. Ten?? en cuenta que <b>rotar
          la cabeza tambi??n cuenta como movimiento</b>. Idealmente durante
          los experimentos tendr??as que estar <b>moviendo ??nicamente tus
          ojos</b>.
        </p>
      </div>`,
      choices: ["continuar"],
    }, {
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <div style="left: calc(50% - 400px); width:800px;">
        <h2>Tutorial</h2>
        <h3>Calibraci??n y validaci??n</h3>
        <p>
          La calibraci??n consiste en fijar la mirada en <b>c??rculos</b> que van
          a aparecer en la pantalla.
          <br>
          Cada vez que aparezca uno ten??s que
        </p>
        <ol>
          <li>fijar la mirada en ??l</li>
          <li>esperar que cambie de color mientras segu??s mir??ndolo</li>
          <li>apenas cambie de color el est??mulo, presionar la <b>barra de
          espacio</b></li>
        </ol>
        <p>
          Luego de cada calibraci??n va a haber otra ronda de est??mulos de
          validaci??n. Con estos vamos a estar verificando los resultados de tu
          calibraci??n anterior. Ten??s que hacer lo mismo: fijar la mirada,
          esperar que cambie de color y presionar la barra de espacio.
        </p>
      </div>`,
      choices: ["continuar"],
    }, {
      type: jsPsychHtmlButtonResponse,
      stimulus: `
      <div style="left: calc(50% - 400px); width:800px;">
        <p>
          As?? que acordate
          <ul>
            <li>prosacada = ${proReminder}</li>
            <li>antisacada = ${antiReminder}</li>
            <li>para calibrar y validar, fij?? la mirada en el c??rculo y
            presion?? la barra de espacio</li>
          </ul>
          <p>
            A continuaci??n toca calibrar el sistema y realizar una serie de
            repeticiones de prueba de ambas tareas.
          </p>
        </p>
      </div>`,
      choices: ["continuar"],
    },
    saccadesBlocksPair({
      n: 10,
      forceCalibration: true,
      isTutorial: true,
    }),
    {
      type: jsPsychHtmlButtonResponse,
      stimulus: retryChoices.html,
      choices: retryChoices.choices,
      on_finish(data) {
        retry = retryChoices.check(data.response);
      },
    }],
    loop_function() {
      return retry;
    }
  };
};

const pause = () => {
  return {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <h3>descanso</h3>
    <p>
      Tomate unos segundos para descansar los ojos y cuando est??s listx hac??
      click en <i>continuar</i>.
    </p>
    `,
    choices: ["continuar"],
  }
}

let breakEarlier = false;
const earlyFinish = {
  html: `
    <div style="left: calc(50% - 400px); width:800px;">
      <p>
        Ah?? llegamos a la mitad del experimento. <br>
        Si todav??a est??s con energ??as hacemos una segunda ronda y si no pod??s
        cortar ac??.
      </p>
    </div>`,
  yes: "cortar ahora",
  no: "seguir con otra ronda",
  get choices() {
    return [this.yes, this.no];
  },
  check(r) {
    return this.yes === this.choices[r]
  },
};
jsPsych.run([
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="left: calc(50% - 400px); width:800px;">
      <h2>Intro</h2>
      <p>
        Bienvenidx a este experimento de eye tracking.
      </p>
  
      <p>
        Utilizando tu c??mara web, vamos a intentar estimar d??nde est??s mirando
        en la pantalla. El experimento va durar aproximadamente 20 minutos.
        Incluye una peque??a introducci??n, un tutorial de unos 5 minutos y luego
        dos bloques de unos 8 minutos. Al final del primer bloque vas a tener la
        opci??n de cortar tempranamente. A lo largo del experimento tambi??n van a
        haber pausas para que puedas descansar la mirada.
        <br>
        El sistema que armamos es muy vulnerable a movimientos de cabeza, por lo 
        que es importante que te sientes c??modx.
      </p>
    </div>
    `,
    choices: ["continuar"],
  },
  {
    type: jsPsychSurveyHtmlForm,
    button_label: 'continuar',
    html: `
    <div style="left: calc(50% - 400px); width:800px;">
      <h2>Intro</h2>
      <p>
        Para arrancar te pedimos este par de datos tuyos y de tu compu.
      </p>
      <ul>
        <li>
          Vas a estar usando anteojos ahora durante el experimento? (si us??s no
          es necesario que te los saques)<br>

          <label for="no-anteojos-input">No</label>
          <input
            type="radio"
            name="anteojos"
            id="no-anteojos-input"
            value="no"
            checked
          >
          &nbsp;

          <label for="anteojos-input">S??</label>
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
          Qu?? datos de hardware sab??s de tu compu? Este campo es informal y
          opcional pero cualquier dato sirve: notebook o compu de escritorio?
          cu??nto RAM ten??s? ten??s placa de video externa? qu?? CPU? tu c??mara web
          es de la notebook o la ten??s aparte? d??nde est?? localizada (a un
          costado, arriba del monitor, abajo del monitor)?<br>

          <input
            type="text"
            name="hardware"
            id="hardware-input"
            size="80"
          >
        </li>
      </ul>
    </div>
    `,
  }, {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="left: calc(50% - 400px); width:800px;">
      <h2>Intro</h2>
      <p>
        En la pr??xima pantalla vamos a activar tu c??mara web. Asegurate de
        tenerla correctamente enchufada y de otorgar los permisos cuando te 
        sean solicitados.
      </p>
    </div>
    `,
    choices: ["continuar"],
  }, {
    type: jsPsychPreload,
    images: ['antisaccade.gif', 'prosaccade.gif'],
  }, {
    type: rastocJSPsych.EventsTrackingStart
  }, {
    type: jsPsychWebgazerInitCamera,
    instructions: `
    <div style="left: calc(50% - 400px); width:800px;">
      <p>
        Correg?? la posici??n de la webcam para que se alinie con tus ojos y estos
        queden bien enfocados. Tu cabeza deber??a quedar en el centro del
        recuadro que aparece ac?? arriba.
        <br>
        Itent?? que tus ojos se distingan correctamente. Si ten??s luces atr??s
        tuyo prob?? apagarlas.
      </p>
      <p>
        Cuando el recuadro se pinte de verde pod??s hacer click en
        <i>"continuar"</i>.
      </p>
    </div>
    `,
    button_text: "continuar"
  }, {
    type: jsPsychFullscreen,
    message: `
    <div style="left: calc(50% - 400px); width:800px;">
      <h2>Intro</h2>
      <p>
        Para evitar distracciones te pedimos tambi??n que en la medida de lo
        posible durante la duraci??n del experimento cierres aplicaciones que
        generen notificaciones y pongas el tel??fono en modo no molestar.
        <br>
        Adem??s vamos a cambiar a pantalla completa.
      </p>
    </div>`,
    button_label: "continuar"
  },
  tutorial(),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <div style="left: calc(50% - 400px); width:800px;">
      <p>
        Ahora arrancan las tareas reales. Presion?? "comenzar" cuando est??s
        listx.
      </p>
    </div>
    `,
    choices: ["comenzar"],
  },
  saccadesBlocksPair(),
  saccadesBlocksPair(),
  pause(),
  saccadesBlocksPair(),
  saccadesBlocksPair(),
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: earlyFinish.html,
    choices: earlyFinish.choices,
    on_finish(data) {
      breakEarlier = earlyFinish.check(data.response);
    },
  },
  {
    conditional_function() {
      return !breakEarlier;
    },
    timeline: [
      displayMsg("Seguimos entonces :)", 2000),
      saccadesBlocksPair(),
      saccadesBlocksPair(),
      pause(),
      saccadesBlocksPair(),
      saccadesBlocksPair(),
    ],
  },
  {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
    <p>
      Fin del experimento. Presion?? <i>finalizar</i> y esper?? unos segundos a
      que la pantalla quede en blanco. Luego pod??s cerrar la pesta??a. <br>
      Muchas gracias por participar c:
    </p>
    `,
    choices: ["finalizar"],
  },
  { type: rastocJSPsych.EventsTrackingStop },
])
