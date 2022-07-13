import matplotlib.pyplot as plt

from common.main import TrialsCollection
from utils.parsing import parse_trials
from utils.constants import EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
from utils.trial_utilities import first_saccade_interval
from fixated_trials import drop_non_fixated_trials
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import drop_early_saccade_trials
from non_response_trials import drop_non_response_trials

CUE = "cue_directed"
NON_CUE = "non_cue_directed"

def divide_trials_by_correctness(trials):
    correct_trials, incorrect_trials = [], []
    for t in trials.all():
        (i, j) = first_saccade_interval(t)
        saccade_x_start = t.estimations[i]['x']
        saccade_x_end = t.estimations[j]['x']
        saccade_direction = \
            CUE if saccade_x_start < saccade_x_end else NON_CUE

        expected_direction = \
            CUE if t.saccade_type == "pro" else NON_CUE

        if saccade_direction == expected_direction:
            correct_trials.append(t)
        else:
            incorrect_trials.append(t)

    return \
        TrialsCollection(correct_trials), \
        TrialsCollection(incorrect_trials)

def drop_incorrect_trials(trials):
    return divide_trials_by_correctness(trials)[0]

if __name__ == "__main__":
    trials = drop_non_fixated_trials(parse_trials()[0])
    compute_saccades_in_place(trials)
    trials = drop_non_response_trials(drop_early_saccade_trials(trials))
    correct_trials, incorrect_trials = divide_trials_by_correctness(trials)

    fig, axes = plt.subplots(nrows=2)
    for j, saccade_type in enumerate(['pro', 'anti']):
        axes[j].set_title("%ssaccades" % saccade_type)
        for t in correct_trials.get_trials_by_saccade(saccade_type):
            es = t['estimates']
            axes[j].plot(
                [e['t'] for e in es],
                [e['x'] for e in es],
                color="black",
                alpha=0.1
            )
        for t in incorrect_trials.get_trials_by_saccade(saccade_type):
            es = t['estimates']
            axes[j].plot(
                [e['t'] for e in es],
                [e['x'] for e in es],
                color="red",
                alpha=0.3
            )
    plt.show()
