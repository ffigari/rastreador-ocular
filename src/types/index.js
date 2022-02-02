export class Point {
  constructor(x, y) {
    if (isNaN(x) || isNaN(y)) {
      throw new Error(
        `Input coordinates are not numbers. Got x=${
          JSON.stringify(x)
        } and y=${
          JSON.stringify(y)
        }`
      );
    }
    this.x = x;
    this.y = y;
  }
  add(xDelta, yDelta) {
    return new Point(this.x + xDelta, this.y + yDelta);
  }
}

export class BBox {
  constructor(origin, width, height) {
    this.origin = origin;  // `origin` is the top left coordinate of the bbox,
                           //  not the center of it
    this.width = width;
    this.height = height;
  }
  get center() {
    return this.origin
      .add(
        Math.round(this.width / 2),
        Math.round(this.height / 2)
      );
  }
  static createResizedFromCenter(bbox, scalingFactor) {
    const { width, height } = bbox;
    const newOrigin = bbox.center.add(
        -(Math.round(scalingFactor * width / 2)),
        -(Math.round(scalingFactor * height / 2))
      );
    return new BBox(
      newOrigin,
      width * scalingFactor,
      height * scalingFactor
    );
  }
  contains(point) {
    const { origin: { x, y }, width, height } = this;
    return (
      x       <= point.x &&
      point.x <= x + width
    ) && (
      y       <= point.y &&
      point.y <= y + height
    );
  }
  get corners() {
    return [
      this.origin,
      this.origin.add(this.width, 0),
      this.origin.add(0, this.height),
      this.origin.add(this.width, this.height),
    ];
  }
}

export class MultiBBox {
  constructor(bboxes) {
    if (bboxes.length === 0) {
      throw new Error(
        `Can not create a multi bbox without bboxes.`
      );
    }
    this.bboxes = bboxes;
  }
  contains(inputBBox) {
    return inputBBox.corners.every((
      corner
    ) => this.bboxes.some(bbox => bbox.contains(corner)));
  }
} 

