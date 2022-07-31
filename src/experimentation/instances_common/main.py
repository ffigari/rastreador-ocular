### figures
import os, sys

sys.path = ['/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'] + sys.path

import matplotlib.pyplot as plt
from instances_common.plots import plot_sampling_frequencies
from instances_common.plots import plot_ages
from instances_common.plots import plot_widths
from instances_common.plots import plot_post_processing_trials
from instances_common.plots import plot_responses_times_distributions
from instances_common.plots import draw_sampling_frequecies_marks
from instances_common.plots import draw_pre_normalization_trials
from instances_common.undetected_saccades import draw_trial_over_ax

from shared.main import rm_rf

def save_fig(figure_name, build_path, logical_path, renderer):
    output_format = "png"
    output_file_name = \
        "{}.{}".format(figure_name, output_format)
    output_file_build_path = \
        "{}/{}".format(build_path, output_file_name)
    output_file_logical_path = \
        "{}/{}".format(logical_path, output_file_name)

    fig = renderer()
    rm_rf(output_file_build_path)
    fig.savefig(output_file_build_path, format=output_format)
    plt.close(fig)  # https://stackoverflow.com/a/9890599/2923526

    return output_file_logical_path

from statistics import mean, stdev

class plot:
    class ages_distribution:
        def __init__(_, ages, instance_tag):
            def renderer():
                return plot_ages(ages)
            save_fig(
                "{}-ages-distribution".format(instance_tag),
                'informe/build/results',
                'results',
                renderer
            )

    class widths_distribution:
        def __init__(_, widths, instance_tag):
            def renderer():
                return plot_widths(widths)
            save_fig(
                "{}-widths-distribution".format(instance_tag),
                'informe/build/results',
                'results',
                renderer
            )

    class sampling_frequencies_distribution:
        def __init__(_, sampling_frequencies, instance_tag):
            def renderer():
                return plot_sampling_frequencies(sampling_frequencies)
            save_fig(
                "{}-sampling-frequencies-distribution".format(instance_tag),
                'informe/build/results',
                'results',
                renderer
            )

    class disaggregated_saccades:
        def __init__(_, categorized_trials, instance_tag, task_tag):
            def renderer():
                return plot_post_processing_trials(
                    categorized_trials[task_tag],
                    'prosacadas' if task_tag == 'pro' else 'antisacadas')
            save_fig(
                '{}-disaggregated-{}saccades'.format(instance_tag, task_tag),
                'informe/build/results',
                'results',
                renderer
            )

    class response_times_distribution:
        def __init__(_, categorized_trials, instance_tag):
            def renderer():
                return plot_responses_times_distributions(
                        categorized_trials,
                        instance_tag)
            save_fig(
                '{}-response-times-distribution'.format(instance_tag),
                'informe/build/results',
                'results',
                renderer
            )

    class frecuency_by_age:
        def __init__(_, starting_sample, instance_tag):
            def renderer():
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
                draw_sampling_frequecies_marks(ax, horizontal=True)
                ax.set_ylabel('frecuencia de muestreo (en Hz)')
                ax.set_xlabel('edad (en años)')

                ax.legend()

                fig.suptitle(
                    'Primera instancia' if instance_tag == 'first' else \
                    'Segunda instancia'
                )

                return fig
            save_fig(
                '{}-sampling-frequencies-by-age'.format(instance_tag),
                'informe/build/results',
                'results',
                renderer
            )

    class undetected_saccade_examples:
        def __init__(_, inlier_sample):
            def renderer():
                fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)
                for ax, (run_id, trial_id), letter in zip(
                        [axes[0][0], axes[0][1], axes[1][0], axes[1][1]],
                        [(105, 225), (68, 267), (76, 504), (96, 332)],
                        ['a', 'b', 'c', 'd']):
                    t = inlier_sample.find_trial(run_id, trial_id)
                    draw_trial_over_ax(ax, t)
                    ax.set_title('{}) run_id={} trial_id={}'.format(
                        letter, t.run_id, t.trial_id))
                [ax.set_xlabel('tiempo (en ms)') for ax in axes[1]]
                fig.subplots_adjust(hspace=0.35)
                return fig

            save_fig(
                'undetected-saccades-examples',
                'informe/build/conclu',
                'conclu',
                renderer
            )

    class skewed_estimations_examples:
        def __init__(_, starting_sample):
            def renderer():
                fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True)

                # primera instancia
                for run_id, ax in [
                    (47, axes[0]),
                    (24, axes[1]),
                    (22, axes[2]),
                    (43, axes[3]),
                ]:
                    draw_pre_normalization_trials(
                        ax,
                        starting_sample.subsample_by_run_id(run_id).ts.all())
                    ax.title.set_text('sujeto {}'.format(run_id))

                handles, labels = (axes[-1]).get_legend_handles_labels()
                fig.legend(handles, labels, loc='lower center')
                fig.set_size_inches(6.4, 8)
                return fig

            save_fig(
                'skewed-estimations-examples',
                'informe/build/metodo',
                'metodo',
                renderer
            )

    class normalization_looks_example:
        def __init__(_, subject_2_44_sample):
            def renderer():
                ts = [
                    t for t in subject_2_44_sample.ts.all()
                    if t.saccade_type == 'anti']

                fig, axes = plt.subplots(nrows=3)

                draw_pre_normalization_trials(axes[0], ts)
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

                fig.subplots_adjust(hspace=0.4)
                fig.legend()
                fig.set_size_inches(6.4, 8)

                return fig

            save_fig(
                'normalization-looks-example',
                'informe/build/metodo',
                'metodo',
                renderer
            )


###

def format_float(f):
    return str((int(f * 100) / 100))

def format_percentage(p):
    return str((int(p * 10000) / 100))

def build_attribute_template(host_name):
    return "{}__{{}}".format(host_name)

def build_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        at.format("trials_count"): sample.trials_count,
        at.format("subjects_count"): sample.subjects_count,
    }

def build_sample_template(instance_name):
    return "{}__{{}}_sample".format(instance_name)

def build_with_response_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        **build_sample_tex_context(sample, sample_name),
        at.format("stdev_response_time"): sample.stdev_response_time,
        at.format("mean_response_time"): sample.mean_response_time,
    }

def build_with_correction_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        **build_with_response_sample_tex_context(sample, sample_name),
        at.format("stdev_correction_delay"): sample.stdev_correction_delay,
        at.format("mean_correction_delay"): sample.mean_correction_delay,
    }

def build_base_instance_tex_context(bi, instance_name):
    st = build_sample_template(instance_name)
    at = build_attribute_template(instance_name)
    return {
        **build_sample_tex_context(bi.starting_sample, st.format("starting")),
        **build_sample_tex_context(bi.inlier_sample, st.format("inlier")),
        **build_with_response_sample_tex_context(bi.correct_sample, st.format("correct")),
        **build_with_response_sample_tex_context(bi.incorrect_sample, st.format("incorrect")),
        at.format("kept_trials_percentage"): \
            format_percentage(bi.inlier_sample.trials_count / bi.starting_sample.trials_count),
        at.format("kept_subjects_percentage"): \
            format_percentage(bi.inlier_sample.subjects_count / bi.starting_sample.subjects_count),
        at.format("antisaccades_correctness_percentage"): \
            format_percentage(bi.antisaccades_correctness_percentage()),
        at.format("antisaccades_correction_percentage"): \
            format_percentage(bi.antisaccades_correction_percentage()),
        at.format("mean_incorrect_antisaccades_count_per_subject"): \
            format_float(bi.mean_incorrect_antisaccades_count_per_subject()),
        **build_with_response_sample_tex_context(
            bi.correct_antisaccades_sample,
            st.format("correct_antisaccades")),
        **build_with_response_sample_tex_context(
            bi.incorrect_antisaccades_sample,
            st.format("incorrect_antisaccades")),
        **build_with_correction_sample_tex_context(
            bi.corrected_antisaccades_sample,
            st.format("corrected_antisaccades")),
    }

