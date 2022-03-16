import matplotlib.pyplot as plt

from utils.main import load_cleaned_up_trials
from utils.main import group_by_run
from utils.main import compute_deviation

trials = [
    t
    for t
    in load_cleaned_up_trials()
    if not t['outlier']
]
trials_by_run = group_by_run(trials)

for t in trials:
    if abs(
        t['mean_fixation_estimation'] - t['run_estimated_center_mean']
    ) > 1 * t['run_estimated_center_stdev']:
        t['outlier'] = True

NROWS = 4
NCOLS = 3
if NROWS * NCOLS < len(trials_by_run):
    raise Exception("Plots grids too small")

fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
for i, (run_id, trials) in enumerate(trials_by_run.items()):
    col = i % NCOLS
    row = i % NROWS
    ax = axs[row][col]
    for t in trials:
        if not t['outlier']:
            continue
        ax.plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="red",
            alpha=0.1
        )
    for t in trials:
        if t['outlier']:
            continue
        ax.plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
plt.show()

# TODO: Center data

# TODO: Move data to range [-1, 1]
