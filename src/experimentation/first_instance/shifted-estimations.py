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

NROWS = 5
NCOLS = 3
if NROWS * NCOLS < len(trials_by_run):
    raise Exception("Plots grids too small")

def plot_center_deviation(ax, trials):
    for t in trials:
        ax.plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
    ax.axhline(
        trials[0]['run_center_x'],
        color="black",
        label="Coordenada x real del centro de la pantalla"
    )
    ax.axhline(
        trials[0]['run_estimated_center_mean'],
        linestyle="--",
        color="red",
        label="Coordenada promedio estimada durante la fase de fijación"
    )

fig, axs = plt.subplots(ncols=NCOLS, nrows=NROWS)
for i, (run_id, trials) in enumerate(trials_by_run.items()):
    col = i % NCOLS
    row = i % NROWS
    ax = axs[row][col]
    plot_center_deviation(ax, trials)
    ax.set_title('Run %d' % run_id)
plt.show()

fix, ax = plt.subplots()
ax.hist(
    [trials[0]['run_deviation_factor'] for _, trials in trials_by_run.items()],
    ec="black"
)
ax.set_title("Histograma de los factores de desviación")
ax.set_ylabel("cantidad de ejecuciones")
ax.set_xlabel("desviación respecto del centro real")
plt.show()

fig, axs = plt.subplots(nrows=2, ncols=2)
for j, runs_ids in enumerate([[47, 24], [43, 22]]):
    for i, run_id in enumerate(runs_ids):
        ax = axs[i][j]
        trials = trials_by_run[run_id]
        plot_center_deviation(ax, trials)
        ax.set_title("run id: %d | desviación: %f" % (
            run_id,
            trials[0]['run_deviation_factor']
        ))
handles, labels = (axs[-1][-1]).get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center')
fig.suptitle('Estimaciones desplazadas')
fig.subplots_adjust(hspace=0.3)
plt.show()
