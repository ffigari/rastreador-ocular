jsPsych.plugins['measure-calibration'] = (function(){
  return {
    info: {
      name: 'measure-calibration',
      parameters: {
      },
    },
    trial: async function(display_element, trial){
      // Una lista de los puntos a usar para la validación en formato <x, y>
      // correspodiente al centro de la sección en porcentaje de la pantalla
      // De momento lo dejo hardcodeado pero se podría ver de armar algo más
      // inteligente para generar las distintas secciones
      const validationSectionsCenters = [
        [25, 25],
        [25, 75],
        [50, 50],
        [75, 25],
        [75, 75],
      ];

      for (const [xPercentage, yPercentage] of validationSectionsCenters) {
        // TODO: Create point
        // TODO: Durante N segundos
        //         depertar cada M milisegundos
        //         guardar donde estoy mirando y la predicción del eye tracker
        await console.log(xPercentage, yPercentage)
      }
      jsPsych.finishTrial();
    },
  }
})();
