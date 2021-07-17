jsPsych.plugins['start-eye-tracking'] = (function(){
  const startGazePredictionVisualization = () => {
    let errorWasInformed = false;
    const visualizationElement = drawer.appendGazeVisualization();
    return [
      visualizationElement.id,
      setInterval(async () => {
        const currentPrediction =
          await jsPsych.extensions.webgazer.getCurrentPrediction();
        if (currentPrediction === null) {
          if (!errorWasInformed) {
            errorWasInformed = true;
            throw new Error(
              `'jsPsych.extensions.webgazer.getCurrentPrediction()' retornó 'null'. Fijate de haber llamado al trial 'webgazer-calibrate'.`
            );
          }
          return;
        }
        drawer.moveToPixels(
          visualizationElement,
          currentPrediction.x,
          currentPrediction.y
        );
      }, 100),
    ];
  };
  return {
    info: {
      name: 'start-eye-tracking',
      parameters: {},
    },
    trial: function(display_element, trial){
      const [
        visualizationElementId,
        loopCallbackIntervalId,
      ] = startGazePredictionVisualization();
      jsPsych.finishTrial({
        visualizationElementId,
        loopCallbackIntervalId,
      });
    },
  };
})();
