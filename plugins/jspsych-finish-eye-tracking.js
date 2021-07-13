jsPsych.plugins['finish-eye-tracking'] = (function(){
  return {
    info: {
      name: 'finish-eye-tracking',
      parameters: {
      },
    },
    trial: function(display_element, trial){
      const eyeTrackingData = JSON.parse(jsPsych.data.get().filter({
        trial_type: 'start-eye-tracking'
      }).json())[0];
      document.getElementById(eyeTrackingData.visualizationElementId).remove();
      clearInterval(eyeTrackingData.loopCallbackIntervalId);
      jsPsych.finishTrial();
    },
  }
})();
