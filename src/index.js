const drawer = (function() {
  return {
    _appendPoint: (id, color, sizeInPixels) => {
      const point = document.createElement('div');
      point.id = id;
      point.style.display = 'block';
      point.style.position = 'fixed';
      point.style.zIndex = 99999;
      point.style.left = `-${sizeInPixels / 2}px`;
      point.style.top  = `-${sizeInPixels / 2}px`;
      point.style.background = color;
      point.style.borderRadius = '100%';
      point.style.opacity = '0.7';
      point.style.width = `${sizeInPixels}px`;
      point.style.height = `${sizeInPixels}px`;
      document.body.appendChild(point);
      return point;
    },
    appendGazeVisualization() {
      return this._appendPoint('gaze-prediction-visualization', 'red', 10);
    },
    appendValidationVisualization() {
      return this._appendPoint('calibration-measurment-visualization', 'black', 30);
    },
    moveToPixels(point, x, y) {
      point.style.transform =
        `translate(${currentPrediction.x}px, ${currentPrediction.y}px)`;
    }
  };
})();

const utils = (function() {
  return {
    sleep: async ms => new Promise(res => setTimeout(res, ms)),
  };
})();
