const getRandomIntInclusive = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const getRandomBoolean = () => {
  return Math.random() < 0.5;
}

const jsPsych = initJsPsych({
  on_finish: function() {
    console.log('fin', jsPsych.data.get())
    //.localSave('json','antisaccades.json');
  }
});

const saccade = ({ anti }) => {
  const showVisualCueAtLeft = getRandomBoolean();
  const durations = {
    interTrial: 950,
    fixation: getRandomIntInclusive(900, 1500),
    intraTrial: 50,
    visualCue: 100,
    responseAwait: 700,
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
  const delta = () => Math.round(2 * window.innerWidth / 6);
  return {
    type: jsPsychPsychophysics,
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
    on_finish(data) {
      // TODO: Si quiero dar feedback en la validación tendría que chequear si
      //       acá ya están las estimaciones, aunque si no llega a estar acá no
      //       sería un problema
      data.isSaccadeExperiment = true;
      data.typeOfSaccade = anti ? 'antisaccade' : 'prosaccade';
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

      // TODO: Acá tendría que chequear el estado de caliración 
    },
  }
};

const REPETITIONS_PER_BLOCK = 2;
const nSaccades = ({ anti }) => {
  const n = REPETITIONS_PER_BLOCK;

  let saccades = [];
  for (let i = 0; i < n; ++i) {
    saccades.push(saccade({ anti }));
  }
  // TODO: Return trial data
  return saccades
};

jsPsych.run([
  { type: jsPsychWebgazerInitCamera },
  { type: rastocJSPsych.EventsTrackingStart },
  {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: "Bloque de prosacada",
    choices: "NO_KEYS",
    trial_duration: 1000,
  },
  rastocJSPsych.ensureCalibration({ performValidation: true }),
  ...nSaccades({ anti: false }),
  {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: "Bloque de antisacada",
    choices: "NO_KEYS",
    trial_duration: 1000,
  },
  rastocJSPsych.ensureCalibration({ performValidation: true }),
  ...nSaccades({ anti: true }),
  { type: rastocJSPsych.EventsTrackingStop }
])
