import random, sys

import matplotlib.pyplot as plt

from data_extraction.main import load_results
from data_extraction.main import SensitivityAnalysis

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
                fig = plot.normalization_effects(subsample).fig
                fig.suptitle('sujeto {}, antisacadas'.format(run_id))
                plt.show()
                plt.close(fig)

    class single_trial_saccades_detection:
        def __init__(_, run_id, trial_id):
            r = load_results()
            t = r.second_instance.inlier_sample.find_trial(run_id, trial_id)
            fig = plot.saccade_detection(t).fig
            plt.show()
            plt.close(fig)

    class saccades_detection:
        def __init__(_):
            r = load_results()
            ts = r.second_instance.inlier_sample.ts.all()
            random.shuffle(ts)
            for t in ts:
                print('>> saccade detection over trial')
                print('instance=second; run_id={}; trial_id={}'.format(
                    t.run_id, t.trial_id))
                fig = plot.saccade_detection(t).fig
                plt.show()
                plt.close(fig)

    class experiment_eye_tracking_summary:
        def __init__(_):
            sa = SensitivityAnalysis()
            fi = sa.first_experiment

            fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)

            # TODO: Plot frequency rolling average and events
            print('start:', fi.start_ts)
            for b in fi.gaze_estimation_blocks:
                es = b.raw_estimations
                print('first: ', es[0]['ts'], ', last: ', es[-1]['ts'])
            [print('calibration start:', ts) for ts in fi.calibrations_starts]
            [print('calibration end:', ts) for ts in fi.calibrations_ends]
            [print('validation start:', ts) for ts in fi.validations_starts]
            [print('validation end:', ts) for ts in fi.validations_ends]
            [print('decalibration:', ts) for ts in fi.decalibration_notifications]
