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
