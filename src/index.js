const eyeTracking = (function() {
  return {
    async currentPrediction() {
      const current =
        await jsPsych.extensions.webgazer.getCurrentPrediction();
      if (current === null) {
        throw new Error(
          `WebGazer retornó 'null' para la predicción actual. Verificar que la librería haya sido correctamente inicializada.`
        );
      }
      return current;
    },
  };
})();

const drawer = (function() {
  return {
    _counter: 1,
    _appendPoint(id, color, sizeInPixels) {
      const point = document.createElement('div');
      point.id = `${id}-${this._counter++}`;
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
    moveToPixels(point, xPixel, yPixel) {
      point.style.transform = `translate(${xPixel}px, ${yPixel}px)`;
    },
    moveToPercentages(point, xPercentage, yPercentage) {
      this.moveToPixels(
        point,
        window.innerWidth  * xPercentage / 100,
        window.innerHeight * yPercentage / 100
      );
    },
    erasePoint(point) {
      document.getElementById(point.id).remove();
    },
  };
})();

const utils = (function() {
  return {
    async sleep(ms ) {
      return new Promise(res => setTimeout(res, ms));
    },
    async runRegularly(maximumDuration, delta, cb) {
      const startingTimestamp = new Date;
      while (true) {
        cb();
        if (new Date - startingTimestamp + delta >= maximumDuration) {
          break;
        }
        await this.sleep(delta);
      }
    }
  };
})();
