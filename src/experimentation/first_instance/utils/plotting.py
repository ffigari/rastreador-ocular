import matplotlib.pyplot as plt

def plot_distinguished_outliers(axs, trials_by_run, NROWS, NCOLS):
    if NROWS * NCOLS < len(trials_by_run):
        raise Exception("Plots grids too small")

    for i, (run_id, run_trials) in enumerate(trials_by_run.items()):
        col = i % NCOLS
        row = i % NROWS
        ax = axs[row][col]
        for t in run_trials:
            if not t['outlier']:
                continue
            ax.plot(
                [e['t'] for e in t['estimations']],
                [e['x'] for e in t['estimations']],
                color="red",
                alpha=0.1,
                label="ensayos descartados"
            )
        for t in run_trials:
            if t['outlier']:
                continue
            ax.plot(
                [e['t'] for e in t['estimations']],
                [e['x'] for e in t['estimations']],
                color="black",
                alpha=0.1,
                label="ensayos conservados"
            )

def show_common_legend(fig, axs):
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
    fig.legend(handles, labels)
