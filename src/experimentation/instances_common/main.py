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

    # This also builds the figure
    def as_tex_string(self, build_path, logical_path):
        output_format = "png"
        output_file_name = \
            "{}.{}".format(self.figure_name, output_format)
        output_file_build_path = \
            "{}/{}".format(build_path, output_file_name)
        output_file_logical_path = \
            "{}/{}".format(logical_path, output_file_name)

        fig = self.render()
        rm_rf(output_file_build_path)
        fig.savefig(output_file_build_path, format=output_format)
        plt.close(fig)  # https://stackoverflow.com/a/9890599/2923526
        
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
        super().__init__ (
            "{}_disaggregated_{}saccades_figure".format(instance_tag, task_tag),
            "{} desagregadas según correctitud y tiempo de respuesta ({} instancia)".format(
                'Antisacadas' if task_tag == 'anti' else 'Prosacadas',
                'primera' if instance_tag == 'first' else 'segunda'
            ),
            "fig:results:{}_disaggregated_{}saccades".format(instance_tag, task_tag),
            "Los ejes temporales de las repeticiones han sido alineados para que el valor t=0 corresponda a la aparición del estímulo visual. Las estimaciones de las coordenadas \'x\' han sido normalizadas al rango [-1, 1]."
        )
        self.categorized_trials = categorized_trials

    def render(self):
        fig = plot_post_processing_trials(self.categorized_trials['anti'], 'antisacadas')
        return fig


class DisaggregatedAntisaccadesFigure(DisaggregatedSaccadesFigure):
    def __init__(self, categorized_trials, instance_tag):
        super().__init__(categorized_trials, instance_tag, 'anti')

class DisaggregatedProsaccadesFigure(DisaggregatedSaccadesFigure):
    def __init__(self, categorized_trials, instance_tag):
        super().__init__(categorized_trials, instance_tag, 'pro')

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

class Sample():
    def __init__(self, ts):
        self.ts = ts
        self.trials_count = ts.count()
        self.subjects_count = ts.subjects_count()

class WithResponseSample(Sample):
    def __init__(self, ts):
        super().__init__(ts)
        rts = [t.response_time for t in ts.all()]
        self.mean_response_time = int(mean(rts))
        self.stdev_response_time = int(stdev(rts))

class Instance():
    def _build_common_tex_context(self, prefix):
        return {
            "{}starting_sample__trials_count".format(prefix): self.starting_sample.trials_count,
            "{}starting_sample__subjects_count".format(prefix): self.starting_sample.subjects_count,
            "{}inlier_sample__trials_count".format(prefix): self.inlier_sample.trials_count,
            "{}inlier_sample__subjects_count".format(prefix): self.inlier_sample.subjects_count,
            "{}without_response_sample__trials_count".format(prefix): self.without_response_sample.trials_count,
            "{}correct_sample__trials_count".format(prefix): self.correct_sample.trials_count,
            "{}incorrect_sample__trials_count".format(prefix): self.incorrect_sample.trials_count,
            "{}correct_sample__mean_response_time".format(prefix): self.correct_sample.mean_response_time,
            "{}correct_sample__stdev_response_time".format(prefix): self.correct_sample.stdev_response_time,
            "{}incorrect_sample__stdev_response_time".format(prefix): self.incorrect_sample.stdev_response_time,
            "{}incorrect_sample__mean_response_time".format(prefix): self.incorrect_sample.mean_response_time,
        }

    def build_tex_context(self):
        # TODO: Build "Instance" tex content here for both instances
        raise NotImplementedError('Instance.build_tex_context')

    def load_data(self):
        raise NotImplementedError('Instance.load_data')

    def process_starting_sample(self, starting_ts):
        raise NotImplementedError('Instance.process_starting_sample')

    def look_for_response(self, inlier_ts):
        raise NotImplementedError('Instance.look_for_response')

    def __init__(self):
        starting_ts = TrialsCollection(self.load_data())
        self.starting_sample = Sample(starting_ts)
        outlier_ts, inlier_ts = self.process_starting_sample(starting_ts)
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
            self.look_for_response(inlier_ts)
        self.without_response_sample = Sample(without_response_ts)
        self.correct_sample = WithResponseSample(correct_ts)
        self.incorrect_sample = WithResponseSample(incorrect_ts)
