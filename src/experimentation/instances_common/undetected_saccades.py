import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from math import ceil

def draw_trial_over_ax(ax, t):
    es = t.estimations
    vs = t.velocities
    for (i, j) in t.saccades_intervals:
        interval_es = es[i:j+1]
        min_x = min([e['x'] for e in interval_es])
        max_x = max([e['x'] for e in interval_es])
        color = 'red' if vs[i]['v'] > 0 else 'blue'
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
        [e['t'] for e in vs],
        [e['v'] for e in vs],
        color='green',
        alpha=0.7,
        marker="2"
    )
    ax.set_ylim([-1.3, 1.3])

def draw_saccade_detection(fig, ax, t):
    draw_trial_over_ax(ax, t)
    fig.suptitle("saccade analysis (run_id=%d; trial_id=%d; saccade_type=%s)" % (
        t.run_id,
        t.trial_id,
        t.saccade_type
    ))
