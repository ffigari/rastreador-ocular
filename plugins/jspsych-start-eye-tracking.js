jsPsych.plugins['start-eye-tracking'] = (function(){
  return {
    info: {
      name: 'start-eye-tracking',
      parameters: {
        showPrediction: {
          type: jsPsych.plugins.parameterType.BOOL,
          default: false,
        }
      },
    },
    trial: function(display_element, trial){
      console.log(trial)
      // TODO: Arrancar el loop para ir actualizando el punto rojo
      // TODO: Ver como se exporta la data
      // TODO: Armar otro plugin que sea `finish-eye-tracking` que corte el
      //       tracking y que ofrece descargar el archivo
      //       Tiene que asegurarse de borrar el punto rojo y de decirle a
      //       webgazer que pare de trackear 
      jsPsych.finishTrial();
    },
  }
})();
