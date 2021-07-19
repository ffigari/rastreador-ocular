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
        const validationPoint = drawer.appendValidationVisualization();
        drawer.moveToPercentages(validationPoint, xPercentage, yPercentage);
        const center = drawer.getCenterInPixels(validationPoint);
        await utils.runRegularly(5000, 100, () => {
          // TODO: Store gaze prediction
          // prediction = await eyeTracking.currentPrediction();
        });
        drawer.erasePoint(validationPoint);
      }
      jsPsych.finishTrial();
    },
  }
})();
