jsPsych.plugins['finish-eye-tracking'] = (function(){
  return {
    info: {
      name: 'finish-eye-tracking',
      parameters: {
      },
    },
    trial: function(display_element, trial){
      // TODO: Armar otro plugin que sea `finish-eye-tracking` que corte el
      //       tracking y que ofrece descargar el archivo
      //       Tiene que asegurarse de borrar el punto rojo y de decirle a
      //       webgazer que pare de trackear 
      console.log(JSON.parse(jsPsych.data.get().json()))
      jsPsych.finishTrial();
    },
  }
})();
