import matplotlib.pyplot as plt

from utils.parsing import parse_trials
from filters import drop_unfocused_trials

trials = drop_unfocused_trials(parse_trials())

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
