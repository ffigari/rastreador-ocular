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
                alpha=0.1
            )
        for t in run_trials:
            if t['outlier']:
                continue
            ax.plot(
                [e['t'] for e in t['estimations']],
                [e['x'] for e in t['estimations']],
                color="black",
                alpha=0.1
            )
