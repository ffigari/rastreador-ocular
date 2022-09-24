import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
import matplotlib.pyplot as plt
from statistics import mean, stdev
from matplotlib.patches import Rectangle
from math import ceil

from data_extraction.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from data_extraction.constants import TARGET_SAMPLING_FREQUENCY_IN_HZ

def separated_hist(ax1, ax2, values, key):
    run_ids = list(set([f['run_id'] for f in values]))
    kept_freqs_run_ids = list(set([f['run_id'] for f in values if f['kept']]))
    dropped_run_ids = [r for r in run_ids if r not in kept_freqs_run_ids]
    for ax, kept_freqs, dropped_freqs in [
        (
            ax1,
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
            [d[key] for d in values if d['kept']],
            [d[key] for d in values if not d['kept']]
        )
    ]:
        ax.hist(
            [kept_freqs, dropped_freqs],
            bins=15,
            ec='black',
            label=['conservadas', 'descartadas']
        )


class draw:
    class sampling_frequecies_marks:
        def __init__(_, ax, horizontal=False):
            f = ax.axhline if horizontal else ax.axvline
            f(
                MINIMUM_SAMPLING_FREQUENCY_IN_HZ,
                linestyle="--",
                color='red',
                alpha=0.3,
                label="frecuencia mínima"
            )
            f(
                TARGET_SAMPLING_FREQUENCY_IN_HZ,
                linestyle="--",
                color='black',
                alpha=0.3,
                label="frecuencia target"
            )
    class pre_normalization_trials:
        def __init__(_, ax, ts):
            for t in ts:
                ax.plot(
                    [e['t'] for e in t.estimations],
                    [e['pre_normalization_x'] for e in t.estimations],
                    color="black",
                    alpha=0.05
                )
            ax.axhline(
                ts[0].run_center_x,
                color="black",
                label="Centro real"
            )
            ax.axhline(
                mean([t.run_estimated_center_mean for t in ts]),
                linestyle="--",
                color="red",
                label="Centro estimado"
            )

    class trial_over_ax:
        def __init__(_, ax, t):
            es = t.estimations
            vs = t.velocities
            for (i, j) in t.saccades_intervals:
                interval_es = es[i:j+1]
                min_x = min([e['x'] for e in interval_es])
                max_x = max([e['x'] for e in interval_es])
                color = 'red' if vs[i]['v'] > 0 else 'blue'
                ax.add_patch(Rectangle(
                    (es[i]['t'], min_x), es[j]['t'] - es[i]['t'], max_x - min_x,
                    color=color, alpha=0.1
                ))
            min_t, max_t = min([e['t'] for e in es]), max([e['t'] for e in es])
            _t = ceil(min_t / 100) * 100
            while _t < max_t:
                alpha = 0.1 if _t != 0 else 0.3
                ax.axvline(_t, color="black", alpha=alpha)
                _t += 100
            ax.axhline(1, color='black', alpha=0.3)
            ax.axhline(0, color='black', alpha=0.3)
            ax.axhline(-1, color='black', alpha=0.3)
            ax.plot(
                [e['t'] for e in es],
                [e['x'] for e in es],
                color='black',
                alpha=0.4,
                marker="1"
            )
            ax.set_ylim([-1.3, 1.3])

class plot:
    class starting_screens_widths:
        def __init__(self, first_sws, second_sws):
            fig, ax = plt.subplots()

            def fn(sws):
                runs_width = dict()
                for d in sws:
                    runs_width[d['run_id']] = d['width']
                return list(runs_width.values())

            ax.hist(
                [fn(first_sws), fn(second_sws)],
                bins=15,
                ec='black',
                label=['Primera instancia', 'Segunda instancia']
            )
            ax.set_ylabel('Cantidad de sujetos')
            ax.set_xlabel('Ancho de pantalla (en píxeles)')
            plt.legend()
            self.fig = fig

    class starting_sampling_frequencies:
        def __init__(self, first_sfs, second_sfs):
            fig, ax = plt.subplots()
            ax.hist(
                [
                    [x['frequency'] for x in first_sfs],
                    [x['frequency'] for x in second_sfs]
                ],
                bins=15,
                ec='black',
                label=['Primera instancia', 'Segunda instancia']
            )
            ax.set_ylabel('Cantidad de ensayos')
            ax.set_xlabel('Frecuencia (en Hz)')
            plt.legend()
            self.fig = fig

    class single_trial:
        class saccades:
            def __init__(self, t):
                fig, ax = plt.subplots()
                draw.trial_over_ax(ax, t)
                ax.set_ylabel('Coordenada x normalizada')
                ax.set_xlabel('Tiempo (en ms)')
                self.fig = fig

        class phases:
            def __init__(self, t):
                fig, ax = plt.subplots()

                es = t.estimations
                pre_n_xs = [e['pre_normalization_x'] for e in es]
                min_x, max_x = min(pre_n_xs), max(pre_n_xs)

                [ax.add_patch(Rectangle(
                    (bot, min_x), top - bot, max_x - min_x,
                    color=color, alpha=0.1, label=label
                )) for (bot, top, color, label) in [
                    (es[0]['t'], t.iti_end, 'red', 'Tiempo entre ensayos'),
                    (t.iti_end, t.fix_end, 'blue', 'Fase de fijación'),
                    (t.fix_end, t.intra_end, 'gray', 'Desaparicion del estímulo'),
                    (t.intra_end, t.response_end, 'green', 'Fase de respuesta'),
                ]]

                # TODO: Idealmente esto debería usar las estimaciones pre
                #       interpolación
                ax.plot(
                    [e['t'] for e in es],
                    pre_n_xs,
                    color='black',
                    alpha=0.4,
                )
                ax.scatter(
                    [e['t'] for e in es],
                    [e['pre_normalization_x'] for e in es],
                    color='black',
                    marker="1"
                )
                ax.axhline(
                    t.run_center_x,
                    color="black",
                    alpha=0.4,
                    linestyle="--"
                )
                ax.set_ylabel('Coordenada horizontal (en píxeles)')
                ax.set_xlabel('Tiempo (en ms)')
                plt.legend()
                self.fig = fig

    # ---

    class normalization_effects:
        def __init__(self, run_subsample):
            fig, axes = plt.subplots(nrows=3)

            ts = [t for t in run_subsample.ts.all() if t.saccade_type == 'anti']

            draw.pre_normalization_trials(axes[0], ts)
            axes[0].set_title('a) aspecto inicial')

            for t in ts:
                axes[1].plot(
                    [e['t'] for e in t.estimations],
                    [e['pre_mirroring_x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            axes[1].set_title('b) aspecto post normalización y pre espejado')

            for t in ts:
                axes[2].plot(
                    [e['t'] for e in t.estimations],
                    [e['x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            axes[2].set_title('c) aspecto final')

            axes[1].set_ylim(-1.5, 1.5)
            axes[2].set_ylim(-1.5, 1.5)
            fig.legend()

            self.fig = fig

    class saccade_detection:
        def __init__(self, trial):
            fig, ax = plt.subplots()
            draw.trial_over_ax(ax, trial)
            fig.suptitle(
                "saccade analysis (run_id=%d; trial_id=%d; saccade_type=%s)" % (
                    trial.run_id,
                    trial.trial_id,
                    trial.saccade_type
                ))

            self.fig = fig

    class post_processing_trials:
        def __init__(self, task_saccades, task_label):
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
                ('correctos', correct_ts), ('incorrectos', incorrect_ts)
            ]):
                axes[0][j].set_title('Ensayos {}'.format(task_result))
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
                'Buckets de {:.2f} ms en base al instante de la primera respuesta'.format(size))

            self.fig = fig

    class responses_times_distributions:
        def __init__(self, trials_results, instance_tag):
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

            fig.suptitle(
                'Primera instancia' if instance_tag == 'first' else \
                'Segunda instancia'
            )

            self.fig = fig

    class ages_distribution:
        def __init__(self, ages):
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

            ax1.set_ylabel('# sujetos')
            ax2.set_ylabel('# ensayos')
            ax2.set_xlabel('edad (en años)')

            separated_hist(ax1, ax2, ages, 'age')
            for ax in [ax1, ax2]:
                ax.legend()

            fig.suptitle('a) Distribución de edades')

            self.fig = fig

    class widths_distribution:
        def __init__(self, widths):
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

            ax1.set_ylabel('# sujetos')
            ax2.set_ylabel('# ensayos')
            ax2.set_xlabel('ancho de pantalla (en píxeles)')

            separated_hist(ax1, ax2, widths, 'width')
            for ax in [ax1, ax2]:
                ax.legend()

            fig.suptitle('b) Distribución de anchos de pantalla')

            self.fig = fig

    class sampling_frequencies_distribution:
        def __init__(self, frequencies):
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

            separated_hist(ax1, ax2, frequencies, 'frequency')

            ax1.set_ylabel('# sujetos')
            ax2.set_ylabel('# ensayos')
            ax2.set_xlabel('frecuencia (en Hz)')

            for ax in [ax1, ax2]:
                draw.sampling_frequecies_marks(ax)

            ax2.legend()

            fig.suptitle('c) Distribución de frecuencias de muestreo originales')

            self.fig = fig


    class frecuency_by_age:
        def __init__(self, starting_sample):
            ts = starting_sample.ts
            def get_age_of(run_id):
                return [
                    t for t in ts.all() if t.run_id == run_id
                ][0].subject_age
            get_frequencies_of = lambda run_id: [
                t.original_sampling_frecuency_in_hz
                for t in ts.all()
                if t.run_id == run_id
            ]
            ages, mean_frequencies, stdev_frequencies = zip(*[(
                v['age'], v['mean'], v['std']
            ) for _, v in dict([(
                run_id, {
                    'age': get_age_of(run_id),
                    'mean': mean(get_frequencies_of(run_id)),
                    'std': stdev(get_frequencies_of(run_id))
                }
            ) for run_id in set([t.run_id for t in ts.all()])]).items()])

            fig, ax = plt.subplots()
            ax.errorbar(
                ages, mean_frequencies, yerr=stdev_frequencies,
                linestyle='None', marker='o', capsize=3,
                label="frecuencia de cada sujeto"
            )
            draw.sampling_frequecies_marks(ax, horizontal=True)
            ax.set_ylabel('frecuencia de muestreo (en Hz)')
            ax.set_xlabel('edad (en años)')

            ax.legend()

            self.fig = fig

    class skewed_estimations_examples:
        def __init__(self, first_starting_sample, compact=False):


            fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True)
            if compact:
                fig, axes = plt.subplots(nrows=1, ncols=2)


            # primera instancia
            runs = [
                (47, axes[0]),
                (43, axes[1]),
            ] if compact else [
                (47, axes[0]),
                (24, axes[1]),
                (22, axes[2]),
                (43, axes[3]),
            ]
            for run_id, ax in runs:
                draw.pre_normalization_trials(
                    ax,
                    first_starting_sample.subsample_by_run_id(run_id).ts.all())
                ax.title.set_text('sujeto {}'.format(run_id))

            handles, labels = (axes[-1]).get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')

            self.fig = fig

    class undetected_saccade_examples:
        def __init__(self, second_inlier_sample):
            fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)
            for ax, (run_id, trial_id), letter in zip(
                    [axes[0][0], axes[0][1], axes[1][0], axes[1][1]],
                    [(105, 225), (68, 267), (76, 504), (96, 332)],
                    ['a', 'b', 'c', 'd']):
                t = second_inlier_sample.find_trial(run_id, trial_id)
                draw.trial_over_ax(ax, t)
                ax.set_title('{}) run_id={} trial_id={}'.format(
                    letter, t.run_id, t.trial_id))
            [ax.set_xlabel('tiempo (en ms)') for ax in axes[1]]

            self.fig = fig
