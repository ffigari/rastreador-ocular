# TODO: Rename file to cooking_tools.py
import sys, os
unwanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
wanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/first_instance'
modified = False
if unwanted in sys.path:
    modified = True
    sys_path_before = list(sys.path)
    sys.path.remove(unwanted)
    sys.path = [wanted] + sys.path

from utils.main import load_cleaned_up_trials
from utils.normalize import normalize
from response_times import drop_invalid_trials
from response_times import mirror_trials
from response_times import compute_correcteness_in_place
from common.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
from constants import POST_NORMALIZATION_REACTION_TRESHOLD
from common.plots import plot_sampling_frequencies
from common.plots import plot_ages
from common.plots import plot_widths
from common.plots import plot_post_processing_trials
from common.plots import plot_responses_times_distributions

if modified:
    sys.path = sys_path_before

###

import os
import matplotlib.pyplot as plt

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

class ResponseTimesDistributionFigure(Figure):
    def __init__(self, saccades):
        super().__init__ ("response_time_distribution",
            "Distribución de tiempos de respuesta",
            "fig:results:rts-distribution",
            "% TODO: Write a comment"
        )
        self.saccades = saccades

    def render(self):
        fig = plot_responses_times_distributions(self.saccades)
        return fig

class DisaggregatedAntisaccadesFigure(Figure):
    def __init__(self, saccades):
        super().__init__ ("disaggregated_antisaccades_figure",
            "Antisacadas desagregadas según correctitud y tiempo de respuesta",
            "fig:results:disaggregated_antisaccades",
            "% TODO: Write a comment"
        )
        self.saccades = saccades

    def render(self):
        fig = plot_post_processing_trials(self.saccades['anti'], 'antisacadas')
        return fig

class AgesDistributionFigure(Figure):
    def __init__(self, ages):
        super().__init__ ("ages_distribution",
            "Distribución de edades",
            "fig:results:ages-distribution",
            "% TODO: Write a comment"
        )

        self.ages = ages

    def render(self):
        fig = plot_ages(self.ages)
        return fig


#####

from statistics import mean, stdev


#####

class Sample():
    def __init__(self, ts):
        self.trials_count = len(ts)
        self.subjects_count = len(list(set([t['run_id'] for t in ts])))

class WithResponseSample(Sample):
    def __init__(self, ts):
        super().__init__(ts)
        rts = [t['reaction_time'] for t in ts]
        self.mean_response_time = int(mean(rts))
        self.stdev_response_time = int(stdev(rts))

def read_normalized_data():
    return mirror_trials(normalize(load_cleaned_up_trials()))

def process_starting_sample(ts):
    trials_pre_processing = drop_invalid_trials([
        t for t in ts if not t['outlier']
    ])

    count_per_run = dict()
    for t in trials_pre_processing:
        if t['run_id'] not in count_per_run:
            count_per_run[t['run_id']] = 0
        count_per_run[t['run_id']] += 1
    trials_with_enough_per_run = [
        t
        for t in trials_pre_processing
        if count_per_run[t['run_id']] >= MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
    ]

    inlier_ts, dropped_trials = [], []
    kept_runs_ids = []
    for t in ts:
        is_kept = len([
            te
            for te in trials_with_enough_per_run
            if te['run_id'] == t['run_id'] and te['trial_id'] == t['trial_id']
        ])
        if is_kept:
            inlier_ts.append(t)
            kept_runs_ids.append(t['run_id'])
        else:
            dropped_trials.append(t)

    outlier_ts = [
        t for t in ts
        if t['id'] not in set([t['id'] for t in inlier_ts])
    ]

    compute_correcteness_in_place(inlier_ts)

    return outlier_ts, inlier_ts

def look_for_response(inlier_ts):
    without_response_ts = [
        t for t in inlier_ts
        if not t['subject_reacted']
    ]
    correct_ts = [
        t for t in inlier_ts
        if t['subject_reacted'] and t['correct_reaction']
    ]
    incorrect_ts = [
        t for t in inlier_ts
        if t['subject_reacted'] and not t['correct_reaction']
    ]
    return without_response_ts, correct_ts, incorrect_ts

class FirstInstanceResults():
    def __init__(self):
        starting_ts = read_normalized_data()
        self.starting_sample = Sample(starting_ts)
        
        outlier_ts, inlier_ts = \
            process_starting_sample(starting_ts)
        self.inlier_sample = Sample(inlier_ts)

        frequencies, ages, widths = [], [], []
        for kept, ts in [(True, inlier_ts), (False, outlier_ts)]:
            for t in ts:
                frequencies.append({
                    'frequency': t['original_sampling_frecuency_in_hz'],
                    'run_id': t['run_id'],
                    'kept': kept,
                })
                ages.append({
                    'age': int(t['subject_data']['edad']),
                    'run_id': t['run_id'],
                    'kept': kept,
                })
                widths.append({
                    'width': t['inner_width'],
                    'run_id': t['run_id'],
                    'kept': kept,
                })

        without_response_ts, correct_ts, incorrect_ts = \
            look_for_response(inlier_ts)
        self.without_response_sample = Sample(without_response_ts)
        self.correct_sample = WithResponseSample(correct_ts)
        self.incorrect_sample = WithResponseSample(incorrect_ts)

        for t in incorrect_ts:
            t['subject_corrected_side'] = False
            for e in t['estimations']:
                if e['t'] < t['reaction_time']:
                    continue
                if e['x'] > - POST_NORMALIZATION_REACTION_TRESHOLD:
                    continue
                t['subject_corrected_side'] = True
                t['correction_reaction_time'] = e['t']
                break
        corrected_ts = [t for t in incorrect_ts if t['subject_corrected_side']]
        self.corrected_sample = WithResponseSample(corrected_ts)

        # TODO: Add remaining summary figures
        self.ages_distribution_figure = AgesDistributionFigure(ages)

        with_response_ts = correct_ts + incorrect_ts
        saccades = {
            'anti': {
                'correct': [{
                    'estimations': [{ 'x': e['x'], 't': e['t'] } for e in t['estimations']],
                    'response_time': t['reaction_time'],
                } for t in with_response_ts if t['correct_reaction']],
                'incorrect': [{
                    'estimations': [{ 'x': e['x'], 't': e['t'] } for e in t['estimations']],
                    'response_time': t['reaction_time'],
                } for t in with_response_ts if not t['correct_reaction']],
            }
        }
        self.response_times_distribution_figure = ResponseTimesDistributionFigure(saccades)
        self.disaggregated_antisaccades_figure = DisaggregatedAntisaccadesFigure(saccades)
