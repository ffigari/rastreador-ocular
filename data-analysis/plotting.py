import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

import matplotlib.pyplot as plt
from statistics import mean
from matplotlib.patches import Rectangle
from math import ceil

class draw:
    class pre_normalization_trials:
        def __init__(_, ax, ts):
            for t in ts:
                ax.plot(
                    [e['t'] for e in t.estimations],
                    [e['pre_normalization_x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            ax.axhline(
                ts[0].run_center_x,
                color="black",
                label="Coordenada x real del centro de la pantalla"
            )
            ax.axhline(
                mean([t.run_estimated_center_mean for t in ts]),
                linestyle="--",
                color="red",
                label="Coordenada promedio estimada durante la fase de fijación"
            )

    class trial_over_ax:
        def __init__(_, ax, t):
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
                alpha=0.4,
                marker="1"
            )
            ax.set_ylim([-1.3, 1.3])


class plot:
    class normalization_effects:
        def __init__(self, run_id, run_subsample):
            fig, axes = plt.subplots(nrows=3)

            ts = [t for t in run_subsample.ts.all() if t.saccade_type == 'anti']

            draw.pre_normalization_trials(axes[0], ts)
            axes[0].set_title('initial look')

            for t in ts:
                axes[1].plot(
                    [e['t'] for e in t.estimations],
                    [e['pre_mirroring_x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            axes[1].set_title('post normalization, pre mirroring')

            for t in ts:
                axes[2].plot(
                    [e['t'] for e in t.estimations],
                    [e['x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            axes[2].set_title('final look')

            axes[1].set_ylim(-1.5, 1.5)
            axes[2].set_ylim(-1.5, 1.5)

            fig.suptitle('sujeto {}, antisacadas'.format(run_id))
            self.fig = fig

    class saccade_detection:
        def __init__(self, trial):
            fig, ax = plt.subplots()
            draw.trial_over_ax(ax, trial)
            fig.suptitle(
                "saccade analysis (run_id=%d; trial_id=%d; saccade_type=%s)" % (
                    t.run_id,
                    t.trial_id,
                    t.saccade_type
                ))

            self.fig = fig
