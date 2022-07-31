def interpolate_between(x, xa, ya, xb, yb):
    # Here x and y are not used as the screen coordinates but as the
    # classic horizontal vs vertical axis.
    # Check https://en.wikipedia.org/wiki/Interpolation#Linear_interpolation
    if not xa <= x <= xb:
        raise Exception('can not interpolate outside of input points')
    return ya + (yb - ya) * (x - xa) / (xb - xa)
