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
from instances_common.plots import draw_trials_with_center
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

                for run_id, ax in [
                    (47, axes[0]),
                    (24, axes[1]),
                    (22, axes[2]),
                    (43, axes[3]),
                ]:
                    draw_trials_with_center(
                        ax,
                        starting_sample.subsample_by_run_id(run_id),
                        run_id)
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

class Trial():
    trials_counter = 0
    def __init__(self,
            run_id,  # `run` and `subjects` are used as synonyms in the code
            trial_id,
            original_sampling_frecuency_in_hz,
            saccade_type,
            estimations,
            subject_age,
            inner_width
        ):
        self.id = Trial.trials_counter
        Trial.trials_counter += 1
        self.run_id = run_id
        self.trial_id = trial_id
        self.original_sampling_frecuency_in_hz = original_sampling_frecuency_in_hz
        self.saccade_type = saccade_type
        self.estimations = estimations
        self.subject_age = subject_age
        self.inner_width = inner_width

class TrialsCollection():
    def __init__(self, ts):
        self.trials = ts
        self.runs_ids = set([t.run_id for t in ts])

    def count(self):
        return len(self.trials)

    def subjects_count(self):
        return len(list(set([t.run_id for t in self.trials])))

    def all(self):
        return self.trials

    def get_trials_by_run_by_saccade(self, run_id, saccade_type):
        return [
            t for t in self.trials
            if t.run_id == run_id and t.saccade_type == saccade_type
        ]

    def get_trials_by_run(self, run_id):
        return TrialsCollection([t for t in self.trials if t.run_id == run_id])

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

optional_milliseconds = lambda t: int(t) if t is not None else None
optional_mean = lambda vs: mean(vs) if len(vs) > 0 else None
optional_stdev = lambda vs: stdev(vs) if len(vs) > 1 else None
o_ms = optional_milliseconds
o_mean = optional_mean
o_stdev = optional_stdev


class Sample():
    def __init__(self, ts):
        self.ts = ts
        self.trials_count = ts.count()
        self.subjects_count = ts.subjects_count()
        trials_count_per_present_subject = [
            ts.get_trials_by_run(run_id).count()
            for run_id
            in set([t.run_id for t in ts.all()])
        ]

        self.mean_trials_count_per_subject = \
            o_mean(trials_count_per_present_subject)
        self.stdev_trials_count_per_subject = \
            o_stdev(trials_count_per_present_subject)

        self.involved_run_ids = set([ t.run_id for t in self.ts.all() ])

    def find_trial(self, run_id, trial_id):
        for t in self.ts.all():
            if t.run_id == run_id and t.trial_id == trial_id:
                return t
        raise RuntimeError(
            'trial of run_id={} and trial_id={} was not found in the sample'.format(
                run_id, trial_id))

    def subsample_by_run_id(self, run_id):
        return Sample(self.ts.get_trials_by_run(run_id))

    def per_subject_subsamples(self):
        return [
            (ri, self.subsample_by_run_id(ri))
            for ri
            in set([t.run_id for t in self.ts.all()])
        ]

def build_with_response_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        **build_sample_tex_context(sample, sample_name),
        at.format("stdev_response_time"): sample.stdev_response_time,
        at.format("mean_response_time"): sample.mean_response_time,
    }

class WithResponseSample(Sample):
    def __init__(self, ts):
        super().__init__(ts)
        rts = [t.response_time for t in ts.all()]
        self.mean_response_time = o_ms(o_mean(rts))
        self.stdev_response_time = o_ms(o_stdev(rts))

def build_with_correction_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        **build_with_response_sample_tex_context(sample, sample_name),
        at.format("stdev_correction_delay"): sample.stdev_correction_delay,
        at.format("mean_correction_delay"): sample.mean_correction_delay,
    }

class WithCorrectionSample(WithResponseSample):
    def __init__(self, incorrect_ts):
        super().__init__(incorrect_ts)
        delays = [t.correction_time - t.response_time for t in incorrect_ts.all()]
        self.mean_correction_delay = o_ms(o_mean(delays))
        self.stdev_correction_delay = o_ms(o_stdev(delays))

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

class PostProcessingMetrics:
    def __init__(self, inlier_sample, outlier_sample):
        self.sampling_frequencies, self.ages, self.widths = [], [], []
        for kept, ts in [(True, inlier_sample.ts), (False, outlier_sample.ts)]:
            for t in ts.all():
                self.sampling_frequencies.append({
                    'frequency': t.original_sampling_frecuency_in_hz,
                    'run_id': t.run_id,
                    'kept': kept,
                })
                self.ages.append({
                    'age': t.subject_age,
                    'run_id': t.run_id,
                    'kept': kept,
                })
                self.widths.append({
                    'width': t.inner_width,
                    'run_id': t.run_id,
                    'kept': kept,
                })

class Instance():
    def mean_incorrect_antisaccades_count_per_subject(self):
        return self.incorrect_antisaccades_sample.mean_trials_count_per_subject

    def antisaccades_correction_percentage(self):
        return \
                self.corrected_antisaccades_sample.trials_count / \
                self.incorrect_antisaccades_sample.trials_count 

    def antisaccades_correctness_percentage(self):
        cas__count = self.correct_antisaccades_sample.trials_count
        return cas__count / (cas__count + self.incorrect_antisaccades_sample.trials_count)

    def _load_data(self):
        raise NotImplementedError('Instance._load_data')

    def _process_starting_sample(self, starting_ts):
        raise NotImplementedError('Instance._process_starting_sample')

    def _look_for_response(self, inlier_ts):
        raise NotImplementedError('Instance._look_for_response')

    def _look_for_corrective_saccade(self, incorrect_ts):
        raise NotImplementedError('Instance._look_for_corrective_saccade')

    def __init__(self):
        starting_ts = TrialsCollection(self._load_data())
        self.starting_sample = Sample(starting_ts)
        outlier_ts, inlier_ts = self._process_starting_sample(starting_ts)
        self.inlier_sample = Sample(inlier_ts)
        self.post_processing_metrics = \
            PostProcessingMetrics(self.inlier_sample, Sample(outlier_ts))

        correct_ts, incorrect_ts = self._look_for_response(inlier_ts)
        self.correct_sample = WithResponseSample(correct_ts)
        self.incorrect_sample = WithResponseSample(incorrect_ts)

        corrected_ts = self._look_for_corrective_saccade(self.incorrect_sample.ts)
        self.corrected_sample = WithCorrectionSample(corrected_ts)
