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
from common.parsing import parse_parsing_callbacks

if modified:
    sys.path = sys_path_before

###

import os
import matplotlib.pyplot as plt

from shared.main import rm_rf

class Figure():
    def __init__(self, build_path, logical_path, figure_name):
        self.build_path = build_path
        self.logical_path = logical_path
        self.figure_name = figure_name

    def render(self):
        raise NotImplementedError(
            'Children of `Figure` need to implement `render` method')

    def export_to_file(self):
        output_format = "png"
        output_file_name = \
            "{}.{}".format(self.figure_name, output_format)
        output_file_build_path = \
            "{}/{}".format(self.build_path, output_file_name)
        output_file_logical_path = \
            "{}/{}".format(self.logical_path, output_file_name)

        fig = self.render()
        rm_rf(output_file_build_path)
        fig.savefig(output_file_build_path, format=output_format)
        plt.close(fig)  # https://stackoverflow.com/a/9890599/2923526

        return output_file_logical_path

class AgesDistributionFigure(Figure):
    def __init__(self, *args):
        super().__init__(*args, "ages_distribution")
        self.comment = "% TODO: Write a comment about ages distribution"
        self.title = "Distribución de edades"

    def render(self):
        fig, _ = plt.subplots()
        fig.suptitle('istribución de edades')
        # TODO
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
    def __init__(self, results_build_path, results_logical_path):
        starting_ts = read_normalized_data()
        self.starting_sample = Sample(starting_ts)
        

        outlier_ts, inlier_ts = \
            process_starting_sample(starting_ts)
        self.inlier_sample = Sample(inlier_ts)

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

        self.ages_distribution_figure = \
            AgesDistributionFigure(results_build_path, results_logical_path)

# TODO: Volar este método
#       En particular no preocuparse en que siga andando
def parse_first_instance(cbs=None):
    cbs = parse_parsing_callbacks(cbs)




    frequencies, ages, widths = [], [], []
    for kept, ts in [(True, inlier_ts), (False, dropped_trials)]:
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

    post_filtering_metrics = dict()
    post_filtering_metrics['frequencies'] = frequencies
    post_filtering_metrics['ages'] = ages
    post_filtering_metrics['widths'] = widths
    cbs['after_filtering'](post_filtering_metrics)

    # TODO: This will be needed to reuse plots later on
    correct_anti = [{
        'estimations': [{ 'x': e['x'], 't': e['t'] } for e in t['estimations']],
        'response_time': t['reaction_time'],
    } for t in trials if t['correct_reaction']]
    incorrect_anti = [{
        'estimations': [{ 'x': e['x'], 't': e['t'] } for e in t['estimations']],
        'response_time': t['reaction_time'],
    } for t in trials if not t['correct_reaction']]

    return {
        'post_filtering_metrics': post_filtering_metrics,
        'saccades': {
            'anti': { 'correct': correct_anti, 'incorrect': incorrect_anti }
        }
    }

def plot_first_post_processing_trials(saccades):
    plot_post_processing_trials(saccades['anti'], 'antisacadas')

if __name__ == "__main__":
    def after_filtering(post_filtering_metrics):
        plot_sampling_frequencies(post_filtering_metrics['frequencies'])
        plot_ages(post_filtering_metrics['ages'])
        plot_widths(post_filtering_metrics['widths'])

    instance = parse_first_instance({ 'after_filtering': after_filtering })
    saccades = instance['saccades']
    plot_first_post_processing_trials(saccades)
    plot_responses_times_distributions(saccades)
