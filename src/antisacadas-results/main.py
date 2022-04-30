import matplotlib.pyplot as plt

from utils.parsing import parse_trials
from fixated_trials import drop_non_fixated_trials
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import drop_early_saccade_trials

def plot_trials_by_run_and_saccade_type(trials):
    fig, axs = plt.subplots(ncols=2, nrows=trials.runs_count)
    for i, run_id in enumerate(trials.runs_ids):
        for j, saccade_type in enumerate(['pro', 'anti']):
            for t in trials.get_trials_by_run_by_saccade(run_id, saccade_type):
                es = t['estimates']
                axs[i][j].plot(
                    [e['t'] for e in es],
                    [e['x'] for e in es],
                    color="black",
                    alpha=0.3
                )
                axs[i][j].set_title("%ssaccades of run %d" % (
                    t['saccade_type'],
                    t['run_id']
                ))
                axs[i][j].axvline(
                    0,
                    linestyle="--",
                    color='black',
                    alpha=0.1,
                    label="apparition of visual cue"
                )
    plt.show()

trials = parse_trials()
original_trials_count = len(trials.all())
# TODO: Count trials per subject too

trials = drop_non_fixated_trials(trials)
plot_trials_by_run_and_saccade_type(trials)
compute_saccades_in_place(trials)

trials = drop_early_saccade_trials(trials)
focused_trials_count = len(trials.all())
print(
    "%d trials out of %d were dropped due to the fixation marker bot being properly fixated before visual cue appeareance" % (
    original_trials_count - focused_trials_count,
    original_trials_count
))
