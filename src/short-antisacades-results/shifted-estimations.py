import random
import matplotlib.pyplot as plt
from datetime import datetime
seed = round(datetime.now().timestamp())
print(
    'The value "%d" was used as a seed, in case you want to repeat the same process later on' % (
    seed
))
random.seed(seed)
from utils import load_trials
from utils import group_by_run
from utils import uniformize_sampling
from utils import center_time_around_visual_cues_start

trials = \
    center_time_around_visual_cues_start(
    uniformize_sampling(
    load_trials()))
NROWS = 3
NCOLS = 2
SHOWN_RUNS_AMOUNT = NCOLS * NROWS  # To show them as a grid
run_ids = list(sorted(set([trial['run_id'] for trial in trials])))
random.shuffle(run_ids)
trials_by_run = group_by_run(trials)

fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
for i, run_id in enumerate(run_ids[:SHOWN_RUNS_AMOUNT]):
    trials = trials_by_run[run_id]
    row = i // NROWS
    col = i // NCOLS
    print(i, row, col, run_id)
plt.show()
