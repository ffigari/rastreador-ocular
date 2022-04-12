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

const saccadeNode = () => {
  // TODO: el intra trial time y el visual cue deberían estar hechos en función
  //       de frames. Se pueden combinar `requestAnimationFrame` y
  //       `performance.now` para estimar el frame rate. Habría que estimarlo
  //       cuando ya esté corriendo todo el sistema. De paso se podría poner un
  //       frame rate mínimo como hacen en TG
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

  const phases = {
    fix: {
      show_start_time: durations.itiEnd,
      show_end_time: durations.fixEnd,
    },
    visual: {
      show_start_time: durations.intraEnd,
      show_end_time: durations.visualEnd,
    },
    response: {
      show_start_time: durations.visualEnd,
      show_end_time: durations.responseEnd,
    },
  };

  // TODO: Esto va a tener que ser anti/pro dependiente
  const fixationMarker = {
    obj_type: 'cross',
    origin_center: true,
    line_length: 30,
  };
  const placeholder = {
    obj_type: 'rect',
    origin_center: true,
    line_color: 'black',
    width: 45,
    height: 45,
    startY: 0,
  }
  const leftPlaceholder = Object.assign({
    startX: -300,
  }, placeholder);
  const rightPlaceholder = Object.assign({
    startX: 300,
  }, placeholder);

  const visualStimulus = {
    obj_type: 'rect',
    origin_center: true,
    fill_color: 'black',
    width: 40,
    height: 40,
    startY: 0,
    startX: 300,
  }

  return {
    type: jsPsychPsychophysics,
    stimuli: [{
      show_start_time: 1000,
      show_end_time: 2500,
      obj_type: 'rect',
      origin_center: true,
      fill_color: 'black',
      width: 40,
      height: 40,
      startY: 0,
      startX: 300,
    }
      //Object.assign({}, phases.fix, fixationMarker),
      //Object.assign({}, phases.fix, rightPlaceholder),
      //Object.assign({}, phases.fix, leftPlaceholder),

      //Object.assign({}, phases.visual, fixationMarker),
      //Object.assign({}, phases.visual, rightPlaceholder),
      //Object.assign({}, phases.visual, leftPlaceholder),
      //Object.assign({}, phases.visual, visualStimulus),

      //Object.assign({}, phases.response, fixationMarker),
      //Object.assign({}, phases.response, rightPlaceholder),
      //Object.assign({}, phases.response, leftPlaceholder),
    ], 
    //trial_duration() {
    //  return durations.total
    //},
  }
}

const REPETITIONS_PER_BLOCK = 20;
let remainingRepetitions = 10;
// TODO: Do all with frame rate
jsPsych.run([
  {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: "qwe",
    trial_duration: 500,
  },
  {
    // TODO: Replace this with the generation of an array of length N so that
    //       I can have the randomized fixation time.
    timeline: [
      saccadeNode(),
    ],
    loop_function() {
      return --remainingRepetitions > 0;
    }
  },
])
