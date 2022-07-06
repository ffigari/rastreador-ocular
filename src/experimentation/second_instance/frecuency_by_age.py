import matplotlib.pyplot as plt
from statistics import mean, stdev

from common.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from common.constants import TARGET_SAMPLING_FREQUENCY_IN_HZ
from utils.parsing import parse_trials
from utils.cleaning import clean

if __name__ == "__main__":
    trials, counts_per_run = parse_trials()

    get_age_of = lambda run_id: [
        t for t in trials.all() if t['run_id'] == run_id
    ][0]['age']
    get_frequencies_of = lambda run_id: [
        t['original_frequency']
        for t in trials.all()
        if t['run_id'] == run_id
    ]
    ages, mean_frequencies, stdev_frequencies = zip(*[(
        v['age'], v['mean'], v['std']
    ) for _, v in dict([(
        run_id, {
            'age': get_age_of(run_id),
            'mean': mean(get_frequencies_of(run_id)),
            'std': stdev(get_frequencies_of(run_id))
        }
    ) for run_id in set([t['run_id'] for t in trials.all()])]).items()])

    fig, ax = plt.subplots()
    ax.errorbar(
        ages, mean_frequencies, yerr=stdev_frequencies,
        linestyle='None', marker='o', capsize=3,
        label="frecuencia de muestreo de cada sujeto"
    )
    ax.axhline(
        MINIMUM_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='red',
        alpha=0.3,
        label="frecuencia mínima de muestreo"
    )
    ax.axhline(
        TARGET_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='black',
        alpha=0.3,
        label="frecuencia objetivo de muestreo"
    )
    ax.set_ylabel('frecuencia de muestreo (en Hz)')
    ax.set_xlabel('edad (en años)')

    ax.legend()
    plt.show()
