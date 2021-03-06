import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from statistics import mean, stdev

from .constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from .constants import TARGET_SAMPLING_FREQUENCY_IN_HZ

def separated_hist(ax1, ax2, values, key):
    run_ids = list(set([f['run_id'] for f in values]))
    kept_freqs_run_ids = list(set([f['run_id'] for f in values if f['kept']]))
    dropped_run_ids = [r for r in run_ids if r not in kept_freqs_run_ids]
    for ax, title, kept_freqs, dropped_freqs in [
        (
            ax1,
            'con repeticiones agrupadas por sujeto',
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
            'con repeticiones miradas individualmente',
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

def draw_sampling_frequecies_marks(ax):
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

def plot_sampling_frequencies(frequencies):
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Distribución de frecuencias de sampleo')

    separated_hist(ax1, ax2, frequencies, 'frequency')

    ax1.set_ylabel('Cantidad de sujetos')
    ax2.set_ylabel('Cantidad de repeticiones')
    ax2.set_xlabel('Frecuencia (en Hz)')

    for ax in [ax1, ax2]:
        draw_sampling_frequecies_marks(ax)

    ax2.legend()
    plt.show()

##
def plot_ages(ages):
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

    ax1.set_ylabel('Cantidad de sujetos')
    ax2.set_ylabel('Cantidad de repeticiones')
    ax2.set_xlabel('Edad')

    separated_hist(ax1, ax2, ages, 'age')
    for ax in [ax1, ax2]:
        ax.legend()
    return fig

def plot_widths(widths):
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Distribución de anchos de pantalla')

    ax1.set_ylabel('Cantidad de sujetos')
    ax2.set_ylabel('Cantidad de repeticiones')
    ax2.set_xlabel('Ancho de pantalla (en píxeles)')

    separated_hist(ax1, ax2, widths, 'width')
    for ax in [ax1, ax2]:
        ax.legend()
    plt.show()

def plot_post_processing_trials(task_saccades, task_label):
    correct_ts = task_saccades['correct']
    incorrect_ts = task_saccades['incorrect']
    BUCKETS_AMOUNT = 5
    max_t = max([
        t.response_time
        for l in [incorrect_ts, correct_ts]
        for t in l])
    axes_with_at_least_one_trial = set()
    fig, axes = plt.subplots(nrows=BUCKETS_AMOUNT, ncols=2, sharex=True)
    for j, (task_result, ts) in enumerate([
        ('correctas', correct_ts), ('incorrectas', incorrect_ts)
    ]):
        axes[0][j].set_title('Repeticiones {}'.format(task_result))
        axes[BUCKETS_AMOUNT - 1][j].set_xlabel('Tiempo (en ms)')
        for t in ts:
            i = min(
                BUCKETS_AMOUNT - 1,
                int(t.response_time // (max_t // BUCKETS_AMOUNT))
            )
            axes[i][j].plot(
                [e['t'] for e in t.estimations],
                [e['x'] for e in t.estimations],
                color="black",
                alpha=0.1
            )
            axes_with_at_least_one_trial.add((i, j))
    size = max_t / BUCKETS_AMOUNT
    ylim = 2
    for (i, j) in axes_with_at_least_one_trial:
        axes[i][j].add_patch(Rectangle(
            (i * size, ylim), size, -(2 * ylim),
            color='red', alpha=0.1
        ))
    [ax.set_ylim([-ylim, ylim]) for axe in axes for ax in axe]
    fig.supylabel(
        'Clasificación en buckets de {:.2f} ms según latencia de la primer respuesta'.format(size))
    return fig

def plot_responses_times_distributions(trials_results):
    min_rt, max_rt = [f([
        t.response_time
        for task_type in trials_results.keys()
        for correcteness in trials_results[task_type].keys()
        for t in trials_results[task_type][correcteness]
    ]) for f in [min, max]]
    buckets_amount = 20
    bucket_size = (max_rt - min_rt) / buckets_amount

    def rt_to_bucket_idx(rt):
        if rt < min_rt:
            raise Exception('rt too low')
        if rt > max_rt:
            raise Exception('rt too low')
        if rt == max_rt:
            return buckets_amount - 1
        return int((rt - min_rt) // bucket_size)

    bucketed_rts = dict()
    for task_type in trials_results.keys():
        bucketed_rts[task_type] = dict()
        for correcteness in trials_results[task_type].keys():
            bucketed_rts[task_type][correcteness] = list()
            for _ in range(buckets_amount):
                bucketed_rts[task_type][correcteness].append(list())
            for rt in [
                t.response_time for t in trials_results[task_type][correcteness]
            ]:
                bucketed_rts[task_type][correcteness][
                    rt_to_bucket_idx(rt)
                ].append(rt)
    buckets_middle_values = [
        ((min_rt + i * bucket_size) + (min_rt + (i + 1) * bucket_size)) / 2
        for i in range(buckets_amount)
    ]

    fig, ax = plt.subplots()
    params = {
        'pro': {
            'correct': {
                'label': 'correct prosaccades',
                'marker': ".",
                'ls': '-'
            },
            'incorrect': {
                'label': 'incorrect prosaccades',
                'marker': "o",
                'ls': '--'
            }
        },
        'anti': {
            'correct': {
                'label': 'correct antisaccades',
                'marker': "x",
                'ls': '-'
            },
            'incorrect': {
                'label': 'incorrect antisaccades',
                'marker': "X",
                'ls': '--'
            }
        },
    }
    for task_type in bucketed_rts.keys():
        for correcteness in bucketed_rts[task_type].keys():
            buckets = bucketed_rts[task_type][correcteness]
            p = params[task_type][correcteness]
            total = sum([len(b) for b in buckets])
            plt.plot(
                buckets_middle_values,
                [len(b) / total for b in buckets],
                label=p['label'],
                color='black',
                lw=0.5,
                ls=p['ls'],
                marker=p['marker']
            )
    ax.set_ylabel('Proporción del total')
    ax.set_xlabel('Tiempo de respuesta (en ms)')
    plt.title(
        'Los tiempos de respuesta han sido divididos en buckets de {:.2f} ms.'.format(
            bucket_size))
    plt.legend()
    return fig
