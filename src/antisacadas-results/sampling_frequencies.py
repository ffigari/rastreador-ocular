import matplotlib.pyplot as plt
from statistics import mean, stdev

from utils.parsing import parse_trials
from common.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from common.constants import TARGET_SAMPLING_FREQUENCY_IN_HZ
from utils.trials_collection import TrialsCollection
from utils.trial_utilities import second_saccade_interval
from fixated_trials import divide_trials_by_focus_on_center
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import divide_trials_by_early_saccade
from non_response_trials import divide_trials_by_non_response
from incorrect_trials import divide_trials_by_correctness
from trials_response_times import compute_response_times_in_place

def divide_trials_by_low_frequency(trials):
    ok_trials, low_frequency_trials = [], []
    for t in trials.all():
        if t[
            'original_frequency'
        ] < MINIMUM_SAMPLING_FREQUENCY_IN_HZ:
            low_frequency_trials.append(t)
        else:
            ok_trials.append(t)


    return \
        TrialsCollection(ok_trials), \
        TrialsCollection(low_frequency_trials)

if __name__ == "__main__":
    trials, counts_per_run = parse_trials()

    fig, (ax1, ax2) = plt.subplots(2, sharex=True)
    fig.suptitle('Obtained sampling frecuencies')

    ax1.set_title('per run\'s mean')
    frequencies_per_run = dict()
    for t in trials.all():
        if t['run_id'] not in frequencies_per_run:
            frequencies_per_run[t['run_id']] = list()
        frequencies_per_run[t['run_id']].append(t['original_frequency'])

    ax1.hist(
        [mean(frequencies) for _, frequencies in frequencies_per_run.items()],
        bins=15,
        ec='black'
    )
    ax1.axvline(
        MINIMUM_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='red',
        alpha=0.3,
        label="minimum sampling frequency"
    )
    ax1.axvline(
        TARGET_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='black',
        alpha=0.3,
        label="target sampling frequency"
    )
    ax1.legend()
    ax1.set_ylabel('runs count')

    ax2.set_title('per trials as a whole')
    ax2.hist(
        [t['original_frequency'] for t in trials.all()],
        bins=15,
        ec='black'
    )
    ax2.axvline(
        MINIMUM_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='red',
        alpha=0.3,
        label="minimum sampling frequency"
    )
    ax2.axvline(
        TARGET_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='black',
        alpha=0.3,
        label="target sampling frequency"
    )
    ax2.set_xlabel('sampling frequency (in Hz)')
    ax2.set_ylabel('trials count')
    plt.show()
