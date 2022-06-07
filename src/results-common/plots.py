import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from statistics import mean, stdev

from common.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from common.constants import TARGET_SAMPLING_FREQUENCY_IN_HZ

def separated_hist(ax1, ax2, values, key):
    run_ids = list(set([f['run_id'] for f in values]))
    kept_freqs_run_ids = list(set([f['run_id'] for f in values if f['kept']]))
    dropped_run_ids = [r for r in run_ids if r not in kept_freqs_run_ids]
    for ax, title, kept_freqs, dropped_freqs in [
        (
            ax1,
            'por sujeto (promediado en base a sus repeticiones)',
            [
                mean([
                    d[key] for d in values if d['run_id'] == run_id
                ]) for run_id in run_ids if run_id not in dropped_run_ids
            ],
            [
                mean([
                    d[key] for d in values if d['run_id'] == run_id
                ]) for run_id in run_ids if run_id in dropped_run_ids
            ]
        ),
        (
            ax2,
            'individualmente por repetición',
            [d[key] for d in values if d['kept']],
            [d[key] for d in values if not d['kept']]
        )
    ]:
        ax.set_title(title)
        ax.hist(
            [kept_freqs, dropped_freqs],
            bins=15,
            ec='black',
            label=['conservadas', 'descartadas']
        )

def plot_sampling_frequencies(frequencies):
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Distribución de frecuencias de sampleo')

    separated_hist(ax1, ax2, frequencies, 'frequency')

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
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Distribución de edades')
    separated_hist(ax1, ax2, ages, 'age')
    for ax in [ax1, ax2]:
        ax.legend()
    plt.show()

def plot_widths(widths):
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Distribución de anchos de pantalla')
    separated_hist(ax1, ax2, widths, 'width')
    for ax in [ax1, ax2]:
        ax.legend()
    plt.show()

def plot_post_processing_trials(correct_ts, incorrect_ts, task_type):
    BUCKETS_AMOUNT = 5
    max_t = max([
        t['response_time']
        for l in [incorrect_ts, correct_ts]
        for t in l])
    axes_with_at_least_one_trial = set()
    fig, axes = plt.subplots(nrows=BUCKETS_AMOUNT, ncols=2, sharex=True)
    fig.suptitle('''Tareas de {}
Los ejes temporales de las repeticiones han sido alineados para que el valor t=0
corresponda a la aparición del estímulo visual. Las estimaciones de las
coordenadas \'x\' han sido normalizadas al rango [-1, 1].'''.format(
        # http://stackoverflow.com/questions/34937048/ddg#44123579
        r"$\bf{" + ('antisacadas' if task_type == 'anti' else 'prosacadas') + "}$"
    ))
    for j, (task_result, ts) in enumerate([
        ('correctas', correct_ts), ('incorrectas', incorrect_ts)
    ]):
        axes[0][j].set_title('Repeticiones {}'.format(task_result))
        axes[BUCKETS_AMOUNT - 1][j].set_xlabel('Tiempo (en ms)')
        for t in ts:
            i = min(
                BUCKETS_AMOUNT - 1,
                int(t[
                    'response_time'
                ] // (max_t // BUCKETS_AMOUNT))
            )
            axes[i][j].plot(
                [e['t'] for e in t['estimations']],
                [e['x'] for e in t['estimations']],
                color="black",
                alpha=0.1
            )
            axes_with_at_least_one_trial.add((i, j))
    size = max_t / BUCKETS_AMOUNT
    for i in range(BUCKETS_AMOUNT):
        axes[i][0].set_ylabel(
            'Estimación de\nla coordenada x\npost normalización\nRespuesta iniciada en\nrango [{:.2f}, {:.2f}] ms'.format(
                i * size,
                (i + 1) * size
            ),
            rotation='horizontal',
            ha='right'
        )
    ylim = 2
    for (i, j) in axes_with_at_least_one_trial:
        axes[i][j].add_patch(Rectangle(
            (i * size, ylim), size, -(2 * ylim),
            color='red', alpha=0.1
        ))
    [ax.set_ylim([-ylim, ylim]) for axe in axes for ax in axe]
    plt.show()
