import matplotlib.pyplot as plt
from utils.main import group_by_run
from utils.main import load_cleaned_up_trials
from utils.plotting import plot_distinguished_outliers

trials = load_cleaned_up_trials()

NROWS = 5
NCOLS = 4
fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
plot_distinguished_outliers(axs, group_by_run(trials), NROWS, NCOLS)
plt.show()
