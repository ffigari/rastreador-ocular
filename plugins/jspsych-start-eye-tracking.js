jsPsych.plugins['start-eye-tracking'] = (function(){
  const startGazePredictionVisualization = () => {
    const visualizationElement = drawer.appendGazeVisualization();
    return [
      visualizationElement.id,
      setInterval(async () => {
        const currentPrediction = await eyeTracking.currentPrediction();
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
