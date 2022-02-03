const jsPsych = initJsPsych({
  on_finish: function() {
    jsPsych.data.get().localSave('json','wg-duration-experiment.json');
  },
  extensions: [
    {type: jsPsychExtensionWebgazer}
  ],
})

const timeline = [{
  type: jsPsychWebgazerInitCamera,
}];

const taskExpectedDurationInSeg = (750 + 750 + 200 + 700) / 1000;
const desiredAmountOfTrials = 4 * 250;
const trialsPerCalibration = Math.max(Math.ceil(desiredAmountOfTrials / 20), 3);
const timeBetweenReportsInSegs = 20;
let startTs;
let lastReportTs;
for (let i = 0; i < desiredAmountOfTrials; i++) {
  if (i % trialsPerCalibration === 0) {
    let calibrated = false;
    const markAsCalibrated = () => {
      calibrated = true;
      document.removeEventListener('click', markAsCalibrated);
    };
    const calibratePoint = ({ clientX, clientY }) => {
      console.log(`mapping <${clientX}, ${clientY}> to gaze`);
      webgazer.recordScreenPosition(clientX, clientY, 'click');
    }
    timeline.push({
      async on_start() {
        if (i === 0) {
          startTs = new Date;
          lastReportTs = new Date;
          webgazer.showPredictionPoints(true);
          await webgazer.resume();
          console.log(`starting trials`);
        }
      },
      type: jsPsychHtmlKeyboardResponse,
      choices: [' '],
      stimulus: `
        <div>
          <h3>Free calibration</h3>
          <p>
            On the next screen you will be allowed to freely calibrate
            WebGazer. Each click you make will map your gaze to the coordinate
            of the click.
            <br>
            As many times as you want, stare at your cursor and perform a
            click. Do this in the regions of the screen you want WebGazer to
            estimate your gaze.
          </p>
          <p>
            You will be shown the gaze estimation while you add calibration
            points. Press <i>Space</i> to start. When you are satisfied press
            <i>Space</i> again to finish the calibration process.
          </p>
        </div>
      `,
    }, {
      timeline: [{
        on_start() {
          console.log('clearing WG data')
          webgazer.clearData();
          document.addEventListener('click', markAsCalibrated);
          document.addEventListener('click', calibratePoint);
        },
        type: jsPsychHtmlKeyboardResponse,
        choices: [' '],
        stimulus: '',
        on_finish() {
          document.removeEventListener('click', markAsCalibrated);
          document.removeEventListener('click', calibratePoint);
        }
      }],
      loop_function() {
        if (!calibrated) {
          console.error('no calibration points were passed')
        }
        return !calibrated;
      }
    });
  }
  preTime = 500 + Math.round(Math.random() * 500);
  fixTime = 500 + Math.round(Math.random() * 500);
  midTime = 150 + Math.round(Math.random() * 100);
  endTime = 700;

  const startX = (Math.random() < 0.5 ? 1 : -1) * Math.floor(window.innerWidth / 3)
  const color = 'blue';
  const radius = 20;
  timeline.push({
    type: jsPsychPsychophysics,
    stimuli: [{
      obj_type: 'text',
      origin_center: true,
      startX: 0, 
      startY: 30,
      show_start_time: 0,
      show_end_time: preTime + fixTime + midTime + endTime,
      content: `${i + 1} / ${desiredAmountOfTrials}`,
    }, {
      obj_type: 'cross',
      origin_center: true,
      startX: 0,
      startY: 0,
      show_start_time: preTime,
      show_end_time: preTime + fixTime,
      line_length: radius * 2,
    }, {
      obj_type: 'circle',
      origin_center: true,
      startX, 
      startY: 0,
      show_start_time:
      preTime + fixTime + midTime,
      show_end_time:
      preTime + fixTime + midTime + endTime,
      radius,
      line_color: color,
      fill_color: color,
    }],
    response_ends_trial: false,
    trial_duration: preTime + fixTime + midTime + endTime,
    extensions: [{ type: jsPsychExtensionWebgazer, params: { targets: [] } }],
    on_finish() {
      if ((new Date - lastReportTs) / 1000 > timeBetweenReportsInSegs) {
        console.log(
          `reached the end of ${
            i + 1
          }-th stimulus; ${
            (
              (new Date - startTs) / 1000
            ).toFixed(2)
          }s elapsed`
        );
        lastReportTs = new Date;
      }
    },
  });
}

console.log(`Task expected duration: ${taskExpectedDurationInSeg}s;
Amount of trials: ${desiredAmountOfTrials};
Experiment expected duration:
  ${((taskExpectedDurationInSeg * desiredAmountOfTrials ) / 60).toFixed(2)} minutes
  + time of one calibration every ${trialsPerCalibration} trials`);

jsPsych.run(timeline);
