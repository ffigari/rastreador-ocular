### figures
import os, sys

sys.path = ['/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'] + sys.path

import matplotlib.pyplot as plt
from instances_common.plots import plot_sampling_frequencies
from instances_common.plots import plot_ages
from instances_common.plots import plot_widths
from instances_common.plots import plot_post_processing_trials
from instances_common.plots import plot_responses_times_distributions

from shared.main import rm_rf

class Figure():
    def __init__(self, figure_name, title, label, comment):
        self.figure_name = figure_name
        self.title = title
        self.label = label
        self.comment = comment

    def render(self):
        raise NotImplementedError(
            'Children of `Figure` need to implement `render` method')

    # TODO: Rename this to `savefig` once all figures tex strings are
    #       moved (back..) to the tex file
    def as_tex_string(self, build_path, logical_path):
        output_file_logical_path = save_fig(
            self.figure_name, build_path, logical_path, self.render)
        
        ctx = {
            "logical_path": output_file_logical_path,
            "label": self.label,
            "comment": self.comment,
            "title": self.title,
        }

        return """
            \\begin{{figure}}
                \\centering
                \\includegraphics{{{logical_path}}}
                \\caption{{{title}}}
                {comment}
                \\label{{{label}}}
            \\end{{figure}}
        """.format(**ctx)

class AgesDistributionFigure(Figure):
    def __init__(self, ages, instance_tag):
        super().__init__(
            "{}_ages_distribution".format(instance_tag),
            "Distribución de edades ({} instancia)".format(
                'primera' if instance_tag == 'first' else 'segunda'
            ),
            "fig:results:{}-ages-distribution".format(instance_tag),
            "% TODO: Write a comment for each instance"
        )
        self.ages = ages

    def render(self):
        fig = plot_ages(self.ages)
        return fig


class ResponseTimesDistributionFigure(Figure):
    def __init__(self, categorized_trials, instance_tag):
        super().__init__(
            "{}_response_time_distribution".format(instance_tag),
            "Distribución de tiempos de respuesta ({} instancia)".format(
                'primera' if instance_tag == 'first' else 'segunda'
            ),
            "fig:results:{}-rts-distribution".format(instance_tag),
            "% TODO: Write a comment"
        )
        self.categorized_trials = categorized_trials

    def render(self):
        fig = plot_responses_times_distributions(self.categorized_trials)
        return fig

class DisaggregatedSaccadesFigure(Figure):
    def __init__(self, categorized_trials, instance_tag, task_tag):
        # TODO: Este __init__ no es necesario porque ahora solo voy a estar
        #       ploteando
        super().__init__ (
            "{}-disaggregated-{}saccades".format(instance_tag, task_tag),
            "{} desagregadas según correctitud y tiempo de respuesta ({} instancia)".format(
                'Antisacadas' if task_tag == 'anti' else 'Prosacadas',
                'primera' if instance_tag == 'first' else 'segunda'
            ),
            "fig:results:{}_disaggregated_{}saccades".format(instance_tag, task_tag),
            "Los ejes temporales de las repeticiones han sido alineados para que el valor t=0 corresponda a la aparición del estímulo visual. Las estimaciones de las coordenadas \'x\' han sido normalizadas al rango [-1, 1]."
        )
        self.categorized_trials = categorized_trials
        self.task_tag = task_tag

    def render(self):
        return render_disaggregated_saccades(self.categorized_trials, self.task_tag)

def render_disaggregated_saccades(categorized_trials, task_tag):
    return plot_post_processing_trials(
            categorized_trials[task_tag],
            'prosacadas' if task_tag == 'pro' else 'antisacadas')

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

class plot:
    class disaggregated_saccades:
        def __init__(self, categorized_trials, instance_tag, task_tag):
            def renderer():
                return render_disaggregated_saccades(categorized_trials, task_tag)
            save_fig(
                '{}-disaggregated-{}saccades'.format(instance_tag, task_tag),
                'informe/build/results',
                'results',
                renderer
            )

#####

from statistics import mean, stdev

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
            mean(trials_count_per_present_subject) \
            if len(trials_count_per_present_subject) > 0 \
            else None
        self.stdev_trials_count_per_subject = \
            stdev(trials_count_per_present_subject) \
            if len(trials_count_per_present_subject) > 1 \
            else None

        self.involved_run_ids = set([ t.run_id for t in self.ts.all() ])

    def subsample_by_run_id(self, run_id):
        return Sample(self.ts.get_trials_by_run(run_id))

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
        self.mean_response_time = int(mean(rts))
        self.stdev_response_time = int(stdev(rts))

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
        self.mean_correction_delay = int(mean(delays))
        self.stdev_correction_delay = int(stdev(delays))

def build_base_instance_tex_context(bi, instance_name):
    st = build_sample_template(instance_name)
    return {
        **build_sample_tex_context(bi.starting_sample, st.format("starting")),
        **build_sample_tex_context(bi.inlier_sample, st.format("inlier")),
        **build_sample_tex_context(bi.without_response_sample, st.format("without_response")),
        **build_with_response_sample_tex_context(bi.correct_sample, st.format("correct")),
        **build_with_response_sample_tex_context(bi.incorrect_sample, st.format("incorrect")),
    }

class Instance():
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

        self.frequencies, self.ages, self.widths = [], [], []
        for kept, ts in [(True, inlier_ts), (False, outlier_ts)]:
            for t in ts.all():
                self.frequencies.append({
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

        without_response_ts, correct_ts, incorrect_ts = \
            self._look_for_response(inlier_ts)
        self.without_response_sample = Sample(without_response_ts)
        self.correct_sample = WithResponseSample(correct_ts)
        self.incorrect_sample = WithResponseSample(incorrect_ts)

        corrected_ts = self._look_for_corrective_saccade(self.incorrect_sample.ts)
        self.corrected_sample = WithCorrectionSample(corrected_ts)
