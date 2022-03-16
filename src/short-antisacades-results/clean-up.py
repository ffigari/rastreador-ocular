import matplotlib.pyplot as plt
from utils.main import group_by_run
from utils.main import load_cleaned_up_trials

trials = load_cleaned_up_trials()

NROWS = 5
NCOLS = 4
SHOWN_RUNS_AMOUNT = NCOLS * NROWS  # To show them as a grid
trials_by_run = group_by_run(trials)
fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
for i, (run_id, trials) in enumerate(trials_by_run.items()):
    if i >= SHOWN_RUNS_AMOUNT:
        break
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
    ax.set_title("%d" % run_id)
plt.show()
