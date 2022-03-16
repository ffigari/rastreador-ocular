import random
import matplotlib.pyplot as plt
from datetime import datetime
seed = round(datetime.now().timestamp())
print(
    'The value "%d" was used as a seed, in case you want to repeat the same process later on' % (
    seed
))
random.seed(seed)
from utils.main import center_time_around_visual_cues_start
from utils.main import group_by_run
from utils.main import load_trials
from utils.main import tag_artifacted_trials
from utils.sampling import tag_low_frecuency_trials
from utils.sampling import uniformize_sampling

trials = \
    tag_artifacted_trials(
    center_time_around_visual_cues_start(
    uniformize_sampling(
    tag_low_frecuency_trials(
    load_trials()))))
NROWS = 5
NCOLS = 4
SHOWN_RUNS_AMOUNT = NCOLS * NROWS  # To show them as a grid
run_ids = list(sorted(set([trial['run_id'] for trial in trials])))
random.shuffle(run_ids)
trials_by_run = group_by_run(trials)

fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
for i, run_id in enumerate(run_ids[:SHOWN_RUNS_AMOUNT]):
    trials = trials_by_run[run_id]
    col = i % NCOLS
    row = i % NROWS
    ax = axs[row][col]
    print('==\n', i, row, col, run_id, len(trials))
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
