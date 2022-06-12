import matplotlib.pyplot as plt

from utils.main import compute_deviation
from utils.main import group_by_run
from utils.main import load_cleaned_up_trials
from utils.normalize import normalize
from utils.plotting import plot_distinguished_outliers

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
fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
plot_distinguished_outliers(axs, trials_by_run, NROWS, NCOLS)
plt.show()

trials = [t for t in trials if not t['outlier']]
trials_by_run = group_by_run(trials)

some_run_ids = [
    run_id
    for i, (run_id, _)
    in enumerate(trials_by_run.items())
    if i < 4
]

fig, axs = plt.subplots(nrows=4, ncols=2)
for i, run_id in enumerate(some_run_ids):
    ax = axs[i][0]
    for t in trials_by_run[run_id]:
        ax.plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
    ax.set_title("run %d before normalization" % run_id)

trials = normalize(trials)
trials_by_run = group_by_run(trials)
for i, run_id in enumerate(some_run_ids):
    ax = axs[i][1]
    for t in trials_by_run[run_id]:
        ax.plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
    ax.set_title("run %d after normalization" % run_id)
plt.show()

fix, ax = plt.subplots()
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
