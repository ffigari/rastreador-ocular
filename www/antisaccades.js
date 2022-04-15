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
    console.log('fin')
    //jsPsych.data.get().localSave('json','antisaccades.json');
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
  const _placeholder = {
    obj_type: 'rect',
    origin_center: true,
    line_color: 'black',
    width: 45,
    height: 45,
    startY: 0,
  }
  const delta = window.innerWidth / 4
  const leftPlaceholder = {
    ..._placeholder,
    startX: - delta,
  }
  const rightPlaceholder = {
    ..._placeholder,
    startX: delta,
  }
  const visualCue = {
    obj_type: 'circle',
    origin_center: true,
    fill_color: 'black',
    radius: 20,
    startY: 0,
    startX: (showVisualCueAtLeft ? -1 : 1) * delta,
  }
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
      show_start_time: durations.itiEnd,
      show_end_time: durations.fixEnd,
      ...leftPlaceholder
    }, {
      show_start_time: durations.intraEnd,
      show_end_time: durations.responseEnd,
      ...leftPlaceholder
    }, {
      show_start_time: durations.itiEnd,
      show_end_time: durations.fixEnd,
      ...rightPlaceholder
    }, {
      show_start_time: durations.intraEnd,
      show_end_time: durations.responseEnd,
      ...rightPlaceholder
    }, {
      show_start_time: durations.intraEnd,
      show_end_time: durations.visualEnd,
      ...visualCue
    }],
    response_ends_trial: false,
    trial_duration: durations.total,
  }
};

const REPETITIONS_PER_BLOCK = 3;
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
  {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: "Bloque de sacada",
    choices: "NO_KEYS",
    trial_duration: 1000,
  },
  ...nSaccades({ anti: false }),
  {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: "Bloque de antisacada",
    choices: "NO_KEYS",
    trial_duration: 1000,
  },
  ...nSaccades({ anti: true }),
])
