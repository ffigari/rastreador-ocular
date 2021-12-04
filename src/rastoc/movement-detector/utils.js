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

export const distance = (p1, p2) => Math.sqrt(
  Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2)
)

export const create = {
  eyePatch: (prediction, keypointsIndexes) => {
    const min = { x: null, y: null }
    const max = { x: null, y: null };
    keypointsIndexes.forEach(keypointIndex => {
      const [x, y, z] = prediction.scaledMesh[keypointIndex];
      min.x = min.x && min.x < x ? min.x : x;
      min.y = min.y && min.y < y ? min.y : y;
      max.x = max.x && max.x > x ? max.x : x;
      max.y = max.y && max.y > y ? max.y : y;
    })
    return {
      min,
      max,
      width: max.x - min.x,
      height: max.y - min.y,
      center: {
        x: (min.x + max.x) / 2,
        y: (min.y + max.y) / 2,
      },
      visualizeAt(ctx, color) {
        ctx.lineWidth = 2;
        ctx.strokeStyle = color || 'black';
        ctx.strokeRect(this.min.x, this.min.y, this.width, this.height);
      },
      get corners() {
        return [
          { x: min.x, y: min.y },
          { x: min.x, y: max.y },
          { x: max.x, y: min.y },
          { x: max.x, y: max.y },
        ]
      }
    };
  },
  eyesPatchsPair: (prediction) => {
    // Los índices de los keypoints pueden consultarse en
    // https://github.com/tensorflow/tfjs-models/blob/master/face-landmarks-detection/mesh_map.jpg
    const [leftEyePatch, rightEyePatch] = [
      [189, 244, 232, 230, 228, 226, 225, 223, 221],
      [413, 464, 452, 450, 448, 446, 445, 443, 441],
    ].map(keypointsIndexes => create.eyePatch(prediction, keypointsIndexes))
    return {
      left: leftEyePatch,
      right: rightEyePatch,
      visualizeAt(ctx, { leftColor, rightColor, color }) {
        [
          [this.left,  leftColor  || color],
          [this.right, rightColor || color],
        ].map(([patch, color]) => patch.visualizeAt(ctx, color))
      },
    };
  },
  validEyePosition: (patches) => {
    const axisCenter = (axis) => {
      return patches
        .map(({ center }) => center[axis])
        .reduce((acc, cur) => acc + cur, 0) / patches.length;
    };
    const center = {
      x: axisCenter('x'),
      y: axisCenter('y'),
    };
    const ratio = patches
    // Collect all corners
      .map(x => x.corners)
    // Flat them into a single array
      .reduce((acc, cur) => acc.concat(cur))
    // Compute each coord's distance to the center of all coordinates
      .map(p => distance(center, p))
    // Find the max distance
      .reduce((acc, cur) => acc > cur ? acc : cur)
    // Add 10% to the resulting value
      * 1.5;
    return {
      contains(eyePatch) {
        return eyePatch.corners.every(c => distance(center, c) <= ratio);
      },
      visualizeAt(ctx, color) {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(center.x, center.y, 3, 0, Math.PI * 2);
        ctx.fill();

        ctx.globalAlpha = 0.3;
        ctx.beginPath();
        ctx.fillStyle = color;
        ctx.arc(center.x, center.y, ratio, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      },
    };
  },
  validEyesPosition: (eyesPatches) => {
    const [leftValidPosition, rightValidPosition] = eyesPatches.reduce((acc, cur) => {
      acc[0].push(cur.left);
      acc[1].push(cur.right);
      return acc;
    }, [[],[]]).map(x => create.validEyePosition(x))
    return {
      visualizeAt(ctx) {
        [[leftValidPosition, 'green'], [rightValidPosition, 'blue']].map(([
          eye, color
        ]) => eye.visualizeAt(ctx, color));
      },
      contains(eyesPair) {
        return leftValidPosition.contains(eyesPair.left)
          && rightValidPosition.contains(eyesPair.right)
      },
    };
  },
}
