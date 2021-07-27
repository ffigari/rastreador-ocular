jsPsych.plugins['measure-calibration'] = (function(){
  return {
    info: {
      name: 'measure-calibration',
      parameters: {
        showPrediction: {
          type: jsPsych.plugins.parameterType.BOOL,
          default: false,
          description: 'si mostrar o no la predicción del eye tracker',
        }
      },
    },
    trial: async function(display_element, trial) {
      trial.showPrediction && eyeTracking.startPredictionVisualization();
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

      const measurements = [];
      for (const [xPercentage, yPercentage] of validationSectionsCenters) {
        const validationPointMeasurements = [];
        const validationPoint = drawer.appendValidationVisualization();
        await drawer.moveInCircleAround(
          validationPoint,
          xPercentage,
          yPercentage,
          5000,
          1000 / 24,
          async (stimulusPoint) => validationPointMeasurements.push({
            prediction: await eyeTracking.currentPrediction(),
            real: drawer.getCenterInPixels(stimulusPoint),
          })
        );
        drawer.erasePoint(validationPoint);
        measurements.push(validationPointMeasurements);
      }
      const individualResults = measurements.map((validationMeasurements) => {
        const distances = validationMeasurements.map(({
          prediction, real
        }) => math.distance(prediction, real));
        return {
          distances,
          mean: math.mean(distances),
          median: math.median(distances),
        };
      });
      const aggregatedResults = {
        meanMean: math.mean(individualResults.map(({ mean }) => mean)),
        meanMedian: math.mean(individualResults.map(({ mean }) => mean)),
      }
      display_element.innerHTML = `
        <div>
          <h4>Resultados</h4>

          <p>
          Los valores presentados están calculados sobre las distancias entre el
          centro del punto y la predicción realizada por el eye tracker.
          </p>

          <h5>Agregados</h5>

          <dl>
            <dt>Promedio del promedio de las distancias</dt>
            <dd>${aggregatedResults.meanMean}</dd>

            <dt>Promedio de las medianas de las distancias</dt>
            <dd>${aggregatedResults.meanMedian}</dd>
          </dl>

          <h5>Por punto</h5>
          <dl>
            <dt>Promedios de las distancias</dt>
            ${individualResults.map(({
              mean
            }) => `<dd>${mean}</dd>`).join("")}

            <dt>Promedios de las medianas</dt>
            ${individualResults.map(({
              median
            }) => `<dd>${median}</dd>`).join("")}
          </dl>
      `
      trial.showPrediction && eyeTracking.stopPredictionVisualization();
      jsPsych.finishTrial();
    },
  }
})();
