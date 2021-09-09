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

const displayHTML = (html) => {
  return {
    at: (element) => {
      return {
        async untilAnyKeyIsPressed() {
          element.innerHTML = html
          const spaceWasPressed = await new Promise((res) => {
            document.addEventListener('keydown', (e) => {
              res(e.code === 'Space')
            })
          })
          element.innerHTML = ''
          return spaceWasPressed
        }
      }
    }
  }
}

const forSingleSpaceBarOn = async (eventTarget) => {
  const handlerResolvedWith = (res) => {
    function handler(e) {
      if (e.code === "Space") {
        eventTarget.removeEventListener('keydown', handler)
        res()
      }
    }
    return handler
  }
  await new Promise((res) => {
    eventTarget.addEventListener('keydown', handlerResolvedWith(res))
  })
}


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
      return this._appendPoint(
        'calibration-measurment-visualization', 'black', 30);
    },
    appendCalibrationStimulus() {
      return this._appendPoint(
        'calibration-stiumulus-visualization', 'blue', 30);
    },
    getCenterInPixels(point) {
      const bbox = point.getBoundingClientRect();
      return [
        (bbox.right + bbox.left) / 2,
        (bbox.bottom + bbox.top) / 2,
      ];
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
