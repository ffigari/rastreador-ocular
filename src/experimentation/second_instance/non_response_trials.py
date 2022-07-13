import matplotlib.pyplot as plt

from common.main import TrialsCollection
from utils.parsing import parse_trials
from utils.trial_utilities import relevant_saccades
from fixated_trials import drop_non_fixated_trials
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import drop_early_saccade_trials

def divide_trials_by_non_response(trials):
    response_trials, non_response_trials = [], []
    for t in trials.all():
        if len(relevant_saccades(t)) > 0:
            response_trials.append(t)
        else:
            non_response_trials.append(t)

    return \
        TrialsCollection(response_trials), \
        TrialsCollection(non_response_trials)

def drop_non_response_trials(trials):
    return divide_trials_by_non_response(trials)[0]

if __name__ == "__main__":
    trials = drop_non_fixated_trials(parse_trials()[0])
    compute_saccades_in_place(trials)
    trials = drop_early_saccade_trials(trials)
    response_trials, non_response_trials = \
        divide_trials_by_non_response(trials)

    fig, ax = plt.subplots()
    for t in response_trials.all():
        es = t['estimates']
        ax.plot(
            [e['t'] for e in es],
            [e['x'] for e in es],
            color="black",
            alpha=0.1
        )
    for t in non_response_trials.all():
        es = t['estimates']
        ax.plot(
            [e['t'] for e in es],
            [e['x'] for e in es],
            color="red",
            alpha=0.3
        )
    plt.show()
