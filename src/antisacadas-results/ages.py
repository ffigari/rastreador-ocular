import matplotlib.pyplot as plt
from statistics import mean, stdev

from utils.parsing import parse_trials
from utils.cleaning import clean

if __name__ == "__main__":
    trials, counts_per_run = parse_trials()

    fig, ax = plt.subplots()
    fig.suptitle('Ages distribution')

    ages_per_run_before_filtering = dict()
    for t in trials.all():
        if t['run_id'] not in ages_per_run_before_filtering:
            ages_per_run_before_filtering[t['run_id']] = t['age']

    trials, counts_per_run = clean(trials, counts_per_run)

    ages_per_run_after_filtering = dict()
    for t in trials.all():
        if t['run_id'] not in ages_per_run_after_filtering:
            ages_per_run_after_filtering[t['run_id']] = t['age']

    ids_of_runs_without_age = [
        k
        for k, a in ages_per_run_before_filtering.items()
        if a is None
    ]
    ages_after_filtering = [
        a
        for _, a in ages_per_run_after_filtering.items()
        if a is not None
    ]
    ages_dropped = [
        a
        for _, a in ages_per_run_before_filtering.items()
        if a is not None and a not in ages_after_filtering
    ]
    ax.hist(
        [ages_after_filtering, ages_dropped],
        bins=15,
        ec='black',
        label=['ages', 'dropped_ages']
    )
    ax.legend()
    # TODO: In the same plot, display dropped and kept runs hist of ages
    # https://stackoverflow.com/questions/6871201/plot-two-histograms-on-single-chart-with-matplotlib
    plt.show()
