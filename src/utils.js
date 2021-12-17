export const Loop = function (mainCb, preMainCb) {
  let inProgress = false;
  const full = async () => {
    await mainCb(preMainCb?.call() || {});
    if (inProgress) {
      go();
    }
  };

  let animationId = null;
  const go = () => {
    animationId = window.requestAnimationFrame(full);
  };
  return {
    get inProgress() {
      return inProgress;
    },
    turn: {
      on() {
        if (inProgress) {
          throw new Error('loop is already turned on.')
        }
        inProgress = true;
        go();
      },
      off() {
        if (!inProgress) {
          throw new Error('loop is already turned off.')
        }
        inProgress = false;
        animationId && window.cancelAnimationFrame(animationId);
        animationId = null;
      },
    },
  };
};

export const canvasDrawer = (function() {
  let _counter = 1
  let _appendPoint = (id, color, sizeInPixels) => {
    const point = document.createElement('div');
    point.id = `${id}-${_counter++}`;
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
  }
  return {
    appendMarkerFor: {
      centerFixation: () => _appendPoint('fixation-marker', 'black', 10),
      antisaccade: {
        target: () => _appendPoint('antisaccade-target', 'black', 30),
        antiSignal: () => _appendPoint('antisaccade-anti-signal', 'red', 30),
        proSignal: () => _appendPoint('antisaccade-pro-signal', 'green', 30),
      },
      gaze: () => _appendPoint('gaze-prediction-visualization', 'red', 10),
      calibration: () => _appendPoint('calibration-stiumulus-visualization', 'blue', 30),
      validation: () => _appendPoint('calibration-measurment-visualization', 'black', 30),
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
    erasePoint(point) {
      document.getElementById(point.id).remove();
    },
    hidePoint(point) {
      document.getElementById(point.id).style.display = 'none';
    },
    showPoint(point) {
      document.getElementById(point.id).style.display = 'block';
    },
  };
})()

export const forSingleSpaceBarOn = async (eventTarget) => {
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
};

export const shuffle = (array) => {
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
};
