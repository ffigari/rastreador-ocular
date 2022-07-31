import matplotlib.pyplot as plt

from common.main import TrialsCollection
from utils.constants import REQUIRED_FOCUS_TIME_PRE_VISUAL_CUE_IN_MS
from utils.constants import EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
from utils.parsing import parse_trials
from fixated_trials import drop_non_fixated_trials
from saccade_detection import compute_saccades_in_place

def drop_early_saccade_trials(trials):
    non_early_saccade_trials, _ = divide_trials_by_early_saccade(trials)
    return non_early_saccade_trials

if __name__ == "__main__":
    trials = drop_non_fixated_trials(parse_trials()[0])
    compute_saccades_in_place(trials)
    non_early_saccade_trials, early_saccade_trials = \
        divide_trials_by_early_saccade(trials)
    fig, ax = plt.subplots()
    for t in non_early_saccade_trials.all():
        es = t['estimates']
        ax.plot(
            [e['t'] for e in es],
            [e['x'] for e in es],
            color="black",
            alpha=0.1
        )
    for t in early_saccade_trials.all():
        es = t['estimates']
        ax.plot(
            [e['t'] for e in es],
            [e['x'] for e in es],
            color="red",
            alpha=0.3
        )
    plt.show()
