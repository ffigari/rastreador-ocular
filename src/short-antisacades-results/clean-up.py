import matplotlib.pyplot as plt

from utils.main import group_by_run
from utils.main import load_cleaned_up_trials
from utils.plotting import plot_distinguished_outliers


trials = load_cleaned_up_trials()

print("%d in total out %d of were marked as outliers" % (
    len([t for t in trials if t["outlier"]]),
    len(trials)
))

NROWS = 5
NCOLS = 4
fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
plot_distinguished_outliers(axs, group_by_run(trials), NROWS, NCOLS)
handles_by_label = dict()
for row_axs in axs:
    for ax in row_axs:
        handles, labels = ax.get_legend_handles_labels()
        for i, l in enumerate(labels):
            if l not in handles_by_label:
                handles_by_label[l] = handles[i]
handles, labels = [], []
for l, h in handles_by_label.items():
    labels.append(l)
    handle, = plt.plot([], [])
    handle.update_from(h)
    handle.set_alpha(1)
    handles.append(handle)
fig.legend(handles, labels, loc='lower center')
fig.suptitle("""Limpieza inicial
Estimaciones de la coordenada x en función del tiempo.
El tiempo 0 se corresponde con la aparición del estímulo visual
""")
plt.show()
