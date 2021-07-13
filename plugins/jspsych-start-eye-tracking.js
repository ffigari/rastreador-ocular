jsPsych.plugins['start-eye-tracking'] = (function(){
  return {
    info: {
      name: 'start-eye-tracking',
      parameters: {
        showPrediction: {
          type: jsPsych.plugins.parameterType.BOOL,
          default: false,
        },
      },
    },
    trial: function(display_element, trial){
      // TODO: Arrancar el loop para ir actualizando el punto rojo
      jsPsych.finishTrial({
        data: 'pimpum',
      });
    },
  };
})();
