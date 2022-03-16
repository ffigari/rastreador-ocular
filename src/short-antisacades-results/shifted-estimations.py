import random
import matplotlib.pyplot as plt
from datetime import datetime
seed = round(datetime.now().timestamp())
print(
    'The value "%d" was used as a seed, in case you want to repeat the same process later on' % (
    seed
))
random.seed(seed)
from utils import load_trials, group_by_run, uniformize_sampling

trials = uniformize_sampling(load_trials())
SHOWN_RUNS_AMOUNT = 2 * 3  # To show them as a grid
run_ids = list(sorted(set([trial['run_id'] for trial in trials])))
random.shuffle(run_ids)
trials_by_run = group_by_run(trials)

fig, axs = plt.subplots(ncols=2, nrows=3)
for i, run_id in enumerate(run_ids[:SHOWN_RUNS_AMOUNT]):
    trials = trials_by_run[run_id]
    print(i, run_id)
plt.show()
