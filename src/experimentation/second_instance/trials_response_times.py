import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from utils.trials_collection import TrialsCollection
from utils.parsing import parse_trials
from utils.trial_utilities import first_saccade_interval
from utils.constants import EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
from common.constants import TARGET_SAMPLING_PERIOD_IN_MS
from fixated_trials import drop_non_fixated_trials
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import drop_early_saccade_trials
from non_response_trials import drop_non_response_trials
from incorrect_trials import drop_incorrect_trials

def compute_response_times_in_place(trials):
    for t in trials.all():
        (i, j) = first_saccade_interval(t)
        t.response_time = t.estimations[i]['t']

if __name__ == "__main__":
    trials = drop_non_fixated_trials(parse_trials()[0])
    compute_saccades_in_place(trials)
    trials = \
        drop_incorrect_trials(
        drop_non_response_trials(
        drop_early_saccade_trials(trials)))
    compute_response_times_in_place(trials)

    buckets_amount = 4

    fig, axes = plt.subplots(nrows=buckets_amount, ncols=2)
    for j, saccade_type in enumerate(['pro', 'anti']):
        responses_range = max([
            t['response_time']
            for t in trials.get_trials_by_saccade(saccade_type)
        ]) \
            - EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS \
            + TARGET_SAMPLING_PERIOD_IN_MS
        bucket_size = responses_range / buckets_amount
        for i in range(buckets_amount):
            bucket_bot = \
                i * bucket_size \
                + EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
            bucket_top = \
                (i + 1) * bucket_size \
                + EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
            axes[i][j].set_title(
                "%ssaccades with response time in [%d, %d]" % (
                saccade_type,
                round(bucket_bot),
                round(bucket_top),
            ))
            relevant_trials = [
                t for t in trials.get_trials_by_saccade(saccade_type)
                if bucket_bot < t['response_time'] <= bucket_top
            ]
            for t in relevant_trials:
                axes[i][j].plot(
                    [e['t'] for e in t['estimates']],
                    [e['x'] for e in t['estimates']],
                    color="black",
                    alpha=0.1
                )
            xs = [
                e['x'] for t in relevant_trials for e in t['estimates']
            ]
            if len(xs) > 0:
                min_x, max_x = min(xs), max(xs)
                axes[i][j].add_patch(Rectangle(
                    (bucket_bot, min_x), bucket_top - bucket_bot, max_x - min_x,
                    color='red', alpha=0.1
                ))
    fig.subplots_adjust(hspace=0.7)
    fig.suptitle("Correct trials")
    plt.show()
