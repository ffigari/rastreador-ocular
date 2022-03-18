import matplotlib.pyplot as plt

from utils.main import group_by_run
from utils.main import load_cleaned_up_trials
from utils.plotting import plot_distinguished_outliers
from utils.plotting import show_common_legend


trials = load_cleaned_up_trials()

print("%d in total out %d of were marked as outliers" % (
    len([t for t in trials if t["outlier"]]),
    len(trials)
))

NROWS = 5
NCOLS = 4
fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
plot_distinguished_outliers(axs, group_by_run(trials), NROWS, NCOLS)
show_common_legend(fig, axs)
fig.suptitle("""Limpieza inicial
Estimaciones de la coordenada x en función del tiempo.
El tiempo 0 se corresponde con la aparición del estímulo visual
""")
plt.show()
