const createLoop = function (display_element) {
  const visualizationElement = document.createElement('div');
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
  document.body.appendChild(visualizationElement)
  return async () => {
    const currentPrediction =
      await jsPsych.extensions.webgazer.getCurrentPrediction();
    visualizationElement.style.transform =
      `translate(${currentPrediction.x}px, ${currentPrediction.y}px)`;
  };
};

jsPsych.plugins['foo-foo'] = (function(){
  return {
    info: {
      name: 'foo-foo',
      parameters: {},
    },
    trial: function(display_element, trial){
      const intervalId = setInterval(createLoop(display_element));
      document.body.onkeyup = (e) => {
        if (e.keyCode === 32) {
          clearInterval(intervalId);
          jsPsych.finishTrial();
        }
      };
    },
  }
})();
