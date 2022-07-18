def compute_saccades_in_place(trials):
    for t in trials.all():
        es = t.estimations
        velocities = [
            {
                't': es[i]['t'],
                'v': es[i + 1]['x'] - es[i]['x']
            } for i in range(len(es) - 1)
        ]

        saccades_intervals = []
        i = 0
        while i < len(velocities):
            j = i
            # first find contiguous intervals with same sign velocity...
            while \
                j + 1 < len(velocities) \
                and velocities[j + 1]['v'] * velocities[i]['v'] > 0:  # same sign?
                j += 1
            if j == i:
                i += 1
                continue

            # ...and then perform some checks
            interval_duration = es[j + 1]['t'] - es[i]['t']
            travelled_distance = abs(es[j + 1]['x'] - es[i]['x'])

            is_long_enough = interval_duration > 40
            travelled_enough_distance = travelled_distance > 0.6
            was_fast_enough = \
                travelled_distance / interval_duration > 0.15 / 100

            if is_long_enough and travelled_enough_distance and was_fast_enough:
                saccades_intervals.append((i, j + 1))
            i = j + 1

        t.saccades_intervals = saccades_intervals
        t.velocities = velocities
