import sys, matplotlib, random
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
from statistics import mean

import matplotlib.pyplot as plt

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
            raise NotImplementedError()
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
