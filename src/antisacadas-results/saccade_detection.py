import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random
from math import ceil

from utils.parsing import parse_trials
from filters import drop_unfocused_trials


def compute_saccades_in_place(trials):
    for t in trials.all():
        es = t['estimates']
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

        t['saccades_intervals'] = saccades_intervals
        t['velocities'] = velocities

if __name__ == "__main__":
    trials = drop_unfocused_trials(parse_trials())
    compute_saccades_in_place(trials)
    tss = trials.all()
    random.shuffle(tss)
    for t in tss:
        es = t['estimates']
        saccades_intervals = t['saccades_intervals']
        velocities = t['velocities']
        fig, ax = plt.subplots()
        print(saccades_intervals)
        for (i, j) in saccades_intervals:
            interval_es = es[i:j+1]
            min_x = min([e['x'] for e in interval_es])
            max_x = max([e['x'] for e in interval_es])
            color = 'red' if velocities[i]['v'] > 0 else 'blue'
            ax.add_patch(Rectangle(
                (es[i]['t'], min_x), es[j]['t'] - es[i]['t'], max_x - min_x,
                color=color, alpha=0.1
            ))
        min_t, max_t = min([e['t'] for e in es]), max([e['t'] for e in es])
        _t = ceil(min_t / 100) * 100
        while _t < max_t:
            alpha = 0.1 if _t != 0 else 0.3
            ax.axvline(_t, color="black", alpha=alpha)
            _t += 100
        ax.axhline(1, color='black', alpha=0.3)
        ax.axhline(0, color='black', alpha=0.3)
        ax.axhline(-1, color='black', alpha=0.3)
        ax.plot(
            [e['t'] for e in es],
            [e['x'] for e in es],
            color='black',
            alpha=0.7,
            marker="1"
        )
        ax.plot(
            [e['t'] for e in velocities],
            [e['v'] for e in velocities],
            color='green',
            alpha=0.7,
            marker="2"
        )
        ax.set_ylim([-1.3, 1.3])
        fig.suptitle("saccade analysis (run_id=%d; trial_id=%d; saccade_type=%s)" % (
            t['run_id'],
            t['trial_id'],
            t['saccade_type']
        ))
        plt.show()
