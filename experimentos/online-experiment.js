// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random#getting_a_random_integer_between_two_values_inclusive
const getRandomIntInclusive = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1) + min);
}
const nNumbers = (n) => [...Array(n).keys()];

jsPsych.init({
  timeline: nNumbers(5).map((trialId) => {
    const foreperiodDuration = getRandomIntInclusive(200, 800);
    const fixationDuration = getRandomIntInclusive(200, 800);
    // Para el RSI tendría sentido hacer una binormal porque en verdad importa
    // estar por arriba o por debajo del valor ese de 200 ms que menciona el 
    // artículo
    const rsiDuration = getRandomIntInclusive(150, 250); 
    const cueDuration = 1000;

    const fixationMarker = {
      obj_type: 'cross',
      origin_center: true,
      startX: 0,
      startY: 0,
      show_start_time: foreperiodDuration,
      show_end_time: foreperiodDuration + fixationDuration,
      line_length: 40,
    };
    const visualCue = {
      obj_type: 'circle',
      origin_center: true,
      startX: 200,
      startY: 0,
      show_start_time: foreperiodDuration + fixationDuration + rsiDuration,
      show_end_time: foreperiodDuration + fixationDuration + rsiDuration + cueDuration,
      radius: 20,
      line_color: 'red',
      fill_color: 'red',
    }

    return {
      type: "psychophysics",
      stimuli: [
        fixationMarker, visualCue,
      ],
      response_ends_trial: false,
      trial_duration:
        foreperiodDuration + fixationDuration + rsiDuration + cueDuration,
    };
  }),
})
