const
  saccadesDurationCeilingInMs = 300,
  elapsedSinceInMs = (ts) => new Date - ts;

const
  timeBetweenUpdatesInMs = 100 + 2 * saccadesDurationCeilingInMs,
  maxAbsX = () => window.innerWidth / 3,
  jsPsych = initJsPsych({
    on_finish() {
      jsPsych.data.get().localSave('csv', 'sensitivity-analysis.csv');
    },
    extensions: [{ type: jsPsychExtensionWebgazer }],
  }),
  budget = {
    experimentTotalBudgetInMs: 3 * 60 * 1000,
    minimumTimePostCalibrationInMs: 10 * 1000,
    startTs: null,
    lastCalibrationTs: null,
    signalyzeExperimentStart() {
      if (this.startTs !== null) {
        throw new Error('Experiment\' start was already signaled.');
      }
      this.startTs = new Date;
    },
    signalyzeCalibration() {
      this.lastCalibrationTs = new Date
    },
    isOver() {
      if (this.startTs === null) {
        throw new Error('Experiment start was never signalyzed.')
      }

      if (this.lastCalibrationTs === null) {
        // At least one calibration should occur
        return false;
      }

      if (
        elapsedSinceInMs(this.lastCalibrationTs) > this.minimumTimePostCalibrationInMs
      ) {
        // Some minimum time is required after a successful calibration
        return false
      }

      if (
        elapsedSinceInMs(this.startTs) < this.experimentTotalBudgetInMs
      ) {
        return false
      }

      return true;
    },
  };
let
  relativeStimulusXCoordinate,
  side;
jsPsych.run([
// TODO: Preguntar sobre el hardware
{
  type: rastocJSPsych.EventsTrackingStart
}, {
  type: jsPsychWebgazerInitCamera,
  on_finish() {
    budget.signalyzeExperimentStart()
    relativeStimulusXCoordinate = 0;
    side = 1;
  },
}, {
  timeline: [rastocJSPsych.ensureCalibration({
    performValidation: true,
    maxRetries: 2,
    postCalibrationCb: () => {
      budget.signalyzeCalibration()
    },
    conditionCb: () => {
      return !budget.isOver();
    },
  }), {
    type: jsPsychPsychophysics,
    stimuli: [{
      show_start_time: 0,
      end_start_time: timeBetweenUpdatesInMs,
      background_color: '#d3d3d3',
      obj_type: 'manual',
      drawFunc: (stim, canvas, ctx) => {
        const cx = Math.round(canvas.width / 2);
        const cy = Math.round(canvas.height / 2);


        ctx.beginPath();
        ctx.arc(cx + relativeStimulusXCoordinate, cy, 16, 0, 2 * Math.PI, false);
        ctx.stroke();

        ctx.beginPath();
        const pre = {
          lineWidth: ctx.lineWidth,
          strokeStyle: ctx.strokeStyle
        };
        ctx.lineWidth = 3;
        ctx.strokeStyle = 'rgb(149, 62, 46)';
        ctx.setLineDash([5, 7]);
        ctx.moveTo(cx + maxAbsX(), cy + 40);
        ctx.lineTo(cx + maxAbsX(), cy - 40);
        ctx.moveTo(cx - maxAbsX(), cy + 40);
        ctx.lineTo(cx - maxAbsX(), cy - 40);
        ctx.stroke();
        ctx.setLineDash([1, 0]);
        Object.assign(ctx, pre)
      },
    }],
    response_ends_trial: false,
    trial_duration: timeBetweenUpdatesInMs,
    extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
    on_finish(data) {
      data.innerWidth = window.innerWidth;

      data.relativeStimulusXCoordinate = relativeStimulusXCoordinate;
      relativeStimulusXCoordinate = relativeStimulusXCoordinate + side * 50;
      const m = maxAbsX();
      const
        overTopLimit = relativeStimulusXCoordinate > m,
        belowBotLimit = relativeStimulusXCoordinate < -m
      if (overTopLimit) relativeStimulusXCoordinate = m;
      if (belowBotLimit) relativeStimulusXCoordinate = -m;
      if (overTopLimit || belowBotLimit) side = -1 * side;
    },
  }],
  loop_function() {
    return !budget.isOver();
  },
}, {
  type: rastocJSPsych.EventsTrackingStop
}
]);
