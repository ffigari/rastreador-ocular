// TODO: Delete
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
  }
})();
