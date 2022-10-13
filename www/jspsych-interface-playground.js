const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('csv','jspsych-playground.csv');
  },
  extensions: [{ type: jsPsychExtensionWebgazer }],
});

const conditionally = {
  showBlankScreen: () => {
    return {
      conditional_function() {
        return getLastChoice().response === 4;
      },
      timeline: [{
        on_start() {
          rastoc.showGazeEstimation();
        },
        type: jsPsychHtmlButtonResponse,
        stimulus: `
          <div>
            <p>
              During this screen your gaze is being estimated using JSPsych's
              WebGazer extension.
            </p>
            <p id="my-paragraph">
              The ID of this pragraph element has been passed to the <a
              href="https://www.jspsych.org/7.1/overview/eye-tracking/#adding-eye-tracking-to-a-trial">
              targets parameter</a> of WebGazer's extension.
            </p>
          </div>`,
        extensions: [{
          type: jsPsychExtensionWebgazer, 
          params: { targets: ['#my-paragraph'] },
        }],
        choices: ['continue'],
        on_finish() {
          rastoc.hideGazeEstimation();
        },
      }],
    }
  },
  calibrate: {
    freely: () => {
      return {
        conditional_function() {
          return getLastChoice().response === 1;
        },
        timeline: [rastocJSPsych.calibrate.freely()],
      }
    },
    middleStrip: () => {
      return {
        conditional_function() {
          return getLastChoice().response === 2;
        },
        timeline: [rastocJSPsych.calibrate.assistedly("middleStrip")],
      }
    },
    fullscreen: () => {
      return {
        conditional_function() {
          return getLastChoice().response === 3;
        },
        timeline: [rastocJSPsych.calibrate.assistedly("fullscreen")],
      }
    },
  },
  showTask: () => {
    return {
      conditional_function() {
        return getLastChoice().response === 5;
      },
      timeline: [
        rastocJSPsych.ensureCalibration({
          calibrationType: "middleStrip",
          performValidation: true,
          maxRetries: 3,
        }), {
          type: jsPsychPsychophysics,
          on_start() {
            rastoc.showGazeEstimation();
          },
          stimuli: [
            {
              obj_type: 'cross',
              origin_center: true,
              get startX() {
                return (Math.random() < 0.5 ? 1 : -1) * (Math.round(Math.random() * 200) + 20);
              },
              startY: 0,
              show_start_time: 100,
              show_end_time: 900,
              line_length: 40,
            },
          ],
          response_ends_trial: false,
          trial_duration: 1000,
          extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
          on_finish() {
            rastoc.hideGazeEstimation();
          },
      }],
      repetitions: 10,
    }
  }
}

const getLastChoice = () => {
  const choices =
    jsPsych.data.get().trials.filter(t => t["rastoc-type"] === 'chosen-path');
  return choices[choices.length - 1];
}

jsPsych.run([{
  type: jsPsychWebgazerInitCamera,
},
{
  type: rastocJSPsych.EventsTrackingStart,
},
{
  timeline: [
    {
      type: jsPsychHtmlButtonResponse,
      stimulus: '<p>What do you want to do next?</p>',
      choices: [
        'finish the experiment',
        'calibrate freely',
        'calibrate middle strip',
        'calibrate fullscreen',
        'show a blank screen',
        'show task while ensuring calibration',
      ],
      on_finish(data) {
        data["rastoc-type"] = 'chosen-path';
      }
    },
    conditionally.calibrate.freely(),
    conditionally.calibrate.middleStrip(),
    conditionally.calibrate.fullscreen(),
    conditionally.showBlankScreen(),
    conditionally.showTask(),
  ],
  loop_function() {
    return getLastChoice().response !== 0;
  },
},
{
  type: rastocJSPsych.EventsTrackingStop,
},
]);
