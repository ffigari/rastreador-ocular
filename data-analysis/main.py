import sys, matplotlib, random
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
from statistics import mean

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from math import ceil

from data_extraction.main import load_results

def draw_pre_normalization_trials(ax, ts):
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
        alpha=0.4,
        marker="1"
    )
    ax.set_ylim([-1.3, 1.3])

def draw_saccade_detection(fig, ax, t):
    draw_trial_over_ax(ax, t)
    fig.suptitle("saccade analysis (run_id=%d; trial_id=%d; saccade_type=%s)" % (
        t.run_id,
        t.trial_id,
        t.saccade_type
    ))


class display:
    class subject_trials:
        def __init__(_):
            r = load_results()
            sst = r.second_instance.starting_sample.per_subject_subsamples()
            random.shuffle(sst)
            for run_id, subsample in sst:
                print('>> subject trials')
                print('run_id={}'.format(run_id))
                fig, axes = plt.subplots(nrows=3)

                ts = [t for t in subsample.ts.all() if t.saccade_type == 'anti']

                draw_pre_normalization_trials(axes[0], ts)
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
                plt.show()
                plt.close(fig)

    class saccades_detection:
        def __init__(_):
            r = load_results()
            def do(t):
                print('>> saccade detection over trial')
                print('run_id={}'.format(t.run_id))
                print('trial_id={}'.format(t.trial_id))

                fig, ax = plt.subplots()
                fig = draw_saccade_detection(fig, ax, t)
                plt.show()
                plt.close(fig)

            sis = r.second_instance.inlier_sample
            if len(sys.argv) > 3:
                run_id = int(sys.argv[3])
                trial_id = int(sys.argv[4])
                t = sis.find_trial(run_id, trial_id)
                do(t)
            else:
                ts = sis.ts.all()
                random.shuffle(ts)
                [do(t) for t in ts]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "An action from [`build`, `display`] has to be chosen",
            file=sys.stderr
        )
        sys.exit(-1)

    if sys.argv[1] == "build":
        raise NotImplementedError()
        sys.exit(0)
    elif sys.argv[1] == "display":
        if len(sys.argv) < 3:
            print(
                "An object from [`subjects-trials`, `saccades-detection`] has to be chosen"
            )
            sys.exit(-1)
        
        if sys.argv[2] == 'subjects-trials':
            display.subject_trials()
            sys.exit(0)
        elif sys.argv[2] == 'saccades-detection':
            display.saccades_detection()
            sys.exit(0)

        print(
            "Invalid object to display, choose one from [`subjects-trials`, `saccades-detection`]",
            file=sys.stderr
        )
        sys.exit(-1)

    print(
        "Invalid action, choose one from [`build`, `display`]",
        file=sys.stderr
    )
    sys.exit(-1)
