import random, sys

import matplotlib.pyplot as plt

from data_extraction.main import load_results
from plotting import draw
from plotting import plot

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
                plt.show()
                plt.close(fig)

    class saccades_detection:
        def __init__(_):
            r = load_results()
            def do(t):
                print('>> saccade detection over trial')
                print('run_id={}'.format(t.run_id))
                print('trial_id={}'.format(t.trial_id))

                fig = plot.saccade_detection(t).fig
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
