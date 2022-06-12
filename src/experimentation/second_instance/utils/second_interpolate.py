def interpolate_with(x, xa, ya, xb, yb):
    # Here x and y are not used as the screen coordinates but as the
    # classic horizontal vs vertical axis.
    # Check https://en.wikipedia.org/wiki/Interpolation#Linear_interpolation
    return ya + (yb - ya) * (x - xa) / (xb - xa)
