const math = (function() {
  return {
    mean(xs) {
      if (xs.length === 0) {
      }
      return xs.reduce((a, b) => a + b) / xs.length;
    },
    median(xs) {
      if (xs.length ===0) {
        throw new TypeError;
      }
      xs = xs.slice().sort((a, b) => a - b);
      const half = Math.floor(xs.length / 2);
      if (xs.length % 2) {
        return xs[half];
      }
      return (xs[half - 1] + xs[half]) / 2.0;
    },
    distance(p1, p2) {
      return this.norm({ x: p1.x - p2.x, y: p1.y - p2.y });
    },
    norm(p) {
      return Math.sqrt(p.x * p.x + p.y * p.y);
    },
    // https://stackoverflow.com/a/2450976/2923526
    shuffle(array) {
      let currentIndex = array.length
      let randomIndex
      while (currentIndex != 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        [
          array[currentIndex], array[randomIndex]
        ] = [
          array[randomIndex], array[currentIndex]
        ];
      }
      return array;
    }
  }
})();

const wgExt = jsPsych.extensions.webgazer

const calibrator = (function () {
  const state = {
    lastCalibrationCoordinates: null
  }
  return {
    get lastCalibrationCoordinates() {
      return state.lastCalibrationCoordinates
    },
    async runExplicitCalibration(
      stimulusDrawer,
      calibrationExtender
    ) {
      let coordinates = [
        [10,10], [10,50], [10,90],
        [50,10], [50,50], [50,90],
        [90,10], [90,50], [90,90],
      ]
      math.shuffle(coordinates)
      state.lastCalibrationCoordinates = [];
      for (const [xGroundTruth, yGroundTruth] of coordinates) {
        // Draw this ground truth coordinate...
        stimulusDrawer(xGroundTruth, yGroundTruth);
        // ...and collect points to map to it
        await calibrationExtender((xEstimated, yEstimated) => {
          wgExt.calibratePoint(xEstimated, yEstimated)
          state.lastCalibrationCoordinates.push([xGroundTruth, yGroundTruth])
        })
      }
    }
  }
})()

const estimator = (function () {
  const state = {
    visualization: {
      isOn: false,
      elementId: null,
      loopCallbackIntervalId: null,
    }
  }
  return {
    async currentPrediction() {
      const current = await wgExt.getCurrentPrediction();
      if (current === null) {
        throw new Error(
          `WebGazer retornó 'null' para la predicción actual. Verificar que la librería haya sido correctamente inicializada.`
        );
      }
      return { x: current.x, y: current.y, };
    },
    showVisualization () {
      if (state.visualization.isOn) {
        throw new Error('La visualización de la estimación ya está activada.');
      }

      const visualizationElement = drawer.appendGazeVisualization();
      const intervalId = setInterval(async () => {
        const currentPrediction = await this.currentPrediction();
        drawer.moveToPixels(
          visualizationElement,
          currentPrediction.x,
          currentPrediction.y
        );
      }, 100)

      Object.assign(state.visualization, {
        isOn: true,
        elementId: visualizationElement.id,
        loopCallbackIntervalId: intervalId,
      });
    },
    hideVisualization() {
      if (!state.visualization.isOn) {
        throw new Error('La visualización de la predicción no está activada.');
      }

      document
        .getElementById(state.visualization.elementId)
        .remove();
      clearInterval(state.visualization.loopCallbackIntervalId);

      Object.assign(state.visualization, {
        isOn: false,
        elementId: null,
        loopCallbackIntervalId: null,
      });
    }
  }
})()

const eyeTracking = (function() {
  const state = {
    phase: 'idle',
    isSurelyUncalibrated: true,
  }
  return {
    get continueTo() {
      return {
        estimate() {
          if (state.phase !== 'estimating') {
            throw new Error(`No se puede continuar estimando por que la fase actual es '${state.phase}'`)
          }
          return estimator
        }
      }
    },
    get switchTo () {
      return {
        idle() {
          if (state.phase === 'idle') {
            throw new Error(`No se pudo cambiar a 'idle' porque la fase ya actual es 'idle'.`)
          }

          Object.assign(state, {
            phase: 'idle',
          })
          wgExt.pause();

          return null
        },
        async calibrating() {
          // TODO: Acá y en estimating habría que agregar un check de que se
          //       haya llamado al plugin que inicializa webgazer
          if (state.phase !== 'idle') {
            throw new Error(`No se pudo cambiar a 'calibrating' porque la fase actual no es 'idle'.`)
          }

          Object.assign(state, {
            phase: 'calibrating',
            isSurelyUncalibrated: false,
          })
          await wgExt.resume();

          return calibrator
        },
        async estimating() {
          const msg = (
            reason
          ) => `No se pudo cambiar a 'estimating' porque ${reason}.`
          if (state.phase !== 'idle') {
            throw new Error(msg(`la fase actual no es 'idle'`))
          }
          if (state.isSurelyUncalibrated) {
            throw new Error(msg(`el sistema no fue calibrado ninguna vez`))
          }

          Object.assign(state, {
            phase: 'estimating',
          })
          await wgExt.resume();

          return estimator
        },
      }
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
    appendCalibrationStimulus() {
      const stimulus = this._appendPoint(
        'calibration-stiumulus-visualization', 'blue', 30)
      stimulus.style.cursor = 'pointer'
      return stimulus;
    },
    getCenterInPixels(point) {
      const bbox = point.getBoundingClientRect();
      return {
        x: (bbox.right + bbox.left) / 2,
        y: (bbox.bottom + bbox.top) / 2,
      };
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
    async moveInCircleAround(
      point, xPer, yPer, maximumDurationInMs, deltaInMs, cb
    ) {
      const radiusInPer = 5;
      const parametrization = (ms) => {
        const angle = 2 * Math.PI * ms / maximumDurationInMs;
        return {
          x: xPer + radiusInPer * Math.cos(angle),
          y: yPer + radiusInPer * Math.sin(angle),
        };
      };
      const updatePoint = (ms) => {
        const positionInCircle = parametrization(ms);
        drawer.moveToPercentages(point, positionInCircle.x, positionInCircle.y);
      };
      updatePoint(0);
      await utils.runRegularly(maximumDurationInMs, deltaInMs, async (
        elapsedTimeInMs
      ) => {
        await cb(point);
        updatePoint(elapsedTimeInMs);
      });
    },
    erasePoint(point) {
      document.getElementById(point.id).remove();
    },
  };
})();

const utils = (function() {
  return {
    async sleep(ms) {
      return new Promise(res => setTimeout(res, ms));
    },
    async runRegularly(maximumDurationInMs, deltaInMs, cb) {
      const startingTimestamp = new Date;
      while (true) {
        const currentElapsedTimeInMs = new Date - startingTimestamp;
        await cb(currentElapsedTimeInMs);

        const nextElapsedTime = currentElapsedTimeInMs + deltaInMs;
        if (nextElapsedTime >= maximumDurationInMs) {
          break;
        }
        await this.sleep(deltaInMs);
      }
    }
  };
})();
