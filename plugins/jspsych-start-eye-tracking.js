jsPsych.plugins['start-eye-tracking'] = (function(){
  const startGazePredictionVisualization = () => {
    let errorWasInformed = false;
    const visualizationElement = document.createElement('div');
    visualizationElement.id = 'gaze-prediction-visualization';
    visualizationElement.style.display = 'block';
    visualizationElement.style.position = 'fixed';
    visualizationElement.style.zIndex = 99999;
    visualizationElement.style.left = '-5px';
    visualizationElement.style.top  = '-5px';
    visualizationElement.style.background = 'red';
    visualizationElement.style.borderRadius = '100%';
    visualizationElement.style.opacity = '0.7';
    visualizationElement.style.width = '10px';
    visualizationElement.style.height = '10px';
    document.body.appendChild(visualizationElement);
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
        visualizationElement.style.transform =
          `translate(${currentPrediction.x}px, ${currentPrediction.y}px)`;
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
