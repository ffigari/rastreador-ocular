import matplotlib.pyplot as plt
import random
from datetime import datetime
seed = round(datetime.now().timestamp())
print(
    'The value "%d" was used as a seed, in case you want to repeat the same process later on' % (
    seed
))
random.seed(seed)

from utils.main import load_cleaned_up_trials
from utils.main import group_by_run

trials = [t for t in load_cleaned_up_trials() if not t['outlier']]
trials_by_run = group_by_run(trials)
print(len(trials_by_run))

NROWS = 5
NCOLS = 3
if NROWS * NCOLS < len(trials_by_run):
    raise Exception("Plots grids too small")

fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
for i, (run_id, trials) in enumerate(trials_by_run.items()):
    col = i % NCOLS
    row = i % NROWS
    ax = axs[row][col]
plt.show()
