import matplotlib.pyplot as plt
from statistics import mean, stdev
from common.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from common.constants import TARGET_SAMPLING_FREQUENCY_IN_HZ

def plot_sampling_frequencies(frequencies):
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Distribución de frecuencias de sampleo')
    run_ids = list(set([f['run_id'] for f in frequencies]))
    kept_freqs_run_ids = list(set([f['run_id'] for f in frequencies if f['kept']]))
    dropped_run_ids = [r for r in run_ids if r not in kept_freqs_run_ids]
    for ax, title, kept_freqs, dropped_freqs in [
        (
            ax1,
            'por sujeto (en base a las frecuencias promedio obtenidas para cada sujeto)',
            [
                mean([
                    d['frequency'] for d in frequencies if d['run_id'] == run_id
                ]) for run_id in run_ids if run_id not in dropped_run_ids
            ],
            [
                mean([
                    d['frequency'] for d in frequencies if d['run_id'] == run_id
                ]) for run_id in run_ids if run_id in dropped_run_ids
            ]
        ),
        (
            ax2,
            'por repetición',
            [d['frequency'] for d in frequencies if d['kept']],
            [d['frequency'] for d in frequencies if not d['kept']]
        )
    ]:
        ax.set_title(title)
        ax.hist(
            [kept_freqs, dropped_freqs],
            bins=15,
            ec='black',
            label=['conservadas', 'descartadas']
        )

    for ax in [ax1, ax2]:
        ax.axvline(
            MINIMUM_SAMPLING_FREQUENCY_IN_HZ,
            linestyle="--",
            color='red',
            alpha=0.3,
            label="frecuencia mínima de sampleo"
        )
        ax.axvline(
            TARGET_SAMPLING_FREQUENCY_IN_HZ,
            linestyle="--",
            color='black',
            alpha=0.3,
            label="frecuencia target de sampleo"
        )
        ax.legend()

    plt.show()

def plot_ages(ages):
    pass

def plot_widths(widths):
    pass
