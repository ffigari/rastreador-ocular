import sys, os
unwanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
wanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/second_instance'
if unwanted in sys.path:
    sys.path.remove(unwanted)
    sys.path = [wanted] + sys.path

from main import drop_runs_without_enough
from utils.parsing import parse_trials
from utils.cleaning import clean
from utils.trials_collection import TrialsCollection
from common.plots import plot_sampling_frequencies
from common.plots import plot_ages
from common.plots import plot_widths
from common.plots import plot_post_processing_trials
from common.plots import plot_responses_times_distributions
from trials_response_times import compute_response_times_in_place
from incorrect_trials import divide_trials_by_correctness
from common.parsing import parse_parsing_callbacks

def parse_second_instance(cbs=None):
    cbs = parse_parsing_callbacks(cbs)

    trials, counts_per_run = parse_trials()
    print('>> Original count: {:d} trials distributed in {:d} subjects'.format(
        trials.count, trials.runs_count
    ))

    trials_pre_processing, counts_per_run = clean(trials, counts_per_run)
    print('>> Pre processing count: {:d} trials distributed in {:d} subjects'.format(
        trials_pre_processing.count, trials_pre_processing.runs_count
    ))

    trials_with_enough_per_run = drop_runs_without_enough(trials_pre_processing, counts_per_run)
    print('>> Pre processing count: {:d} trials distributed in {:d} subjects'.format(
        trials_with_enough_per_run.count, trials_with_enough_per_run.runs_count
    ))

    kept_trials, dropped_trials = [], []
    kept_runs_ids = []
    for t in trials.all():
        is_kept = len([
            te
            for te in trials_with_enough_per_run.all()
            if te['run_id'] == t['run_id'] and te['trial_id'] == t['trial_id']
        ])
        if is_kept:
            kept_trials.append(t)
            kept_runs_ids.append(t['run_id'])
        else:
            dropped_trials.append(t)
    print('>> {:.2f} % of trials dropped; {:.2f} % of runs dropped'.format(
        100 * (len(dropped_trials) / len(trials.all())),
        100 * (
            (len(set([t['run_id'] for t in trials.all()])) - len(set(kept_runs_ids))) \
            / len(set([t['run_id'] for t in trials.all()]))
        )
    ))

    frequencies, ages, widths = [], [], []
    for kept, ts in [(True, kept_trials), (False, dropped_trials)]:
        for t in ts:
            frequencies.append({
                'frequency': t['original_frequency'],
                'run_id': t['run_id'],
                'kept': kept,
            })
            ages.append({
                'age': t['age'],
                'run_id': t['run_id'],
                'kept': kept,
            })
            widths.append({
                'width': t['viewport_width'],
                'run_id': t['run_id'],
                'kept': kept,
            })

    post_filtering_metrics = dict()
    post_filtering_metrics['frequencies'] = frequencies
    post_filtering_metrics['ages'] = ages
    post_filtering_metrics['widths'] = widths
    cbs['after_filtering'](post_filtering_metrics)

    trials = TrialsCollection(kept_trials)
    compute_response_times_in_place(trials)
    correct_trials, incorrect_trials = divide_trials_by_correctness(trials)
    correct_anti = [{
        'estimations': t['estimates'],
        'response_time': t['response_time']
    } for t in correct_trials.all() if t['saccade_type'] == "anti"]
    incorrect_anti = [{
        'estimations': t['estimates'],
        'response_time': t['response_time']
    } for t in incorrect_trials.all() if t['saccade_type'] == "anti"]
    correct_pro = [{
        'estimations': t['estimates'],
        'response_time': t['response_time']
    } for t in correct_trials.all() if t['saccade_type'] == "pro"]
    incorrect_pro = [{
        'estimations': t['estimates'],
        'response_time': t['response_time']
    } for t in incorrect_trials.all() if t['saccade_type'] == "pro"]
    return {
        'post_filtering_metrics': post_filtering_metrics,
        'saccades': {
            'anti': {
                'correct': correct_anti,
                'incorrect': incorrect_anti,
            },
            'pro': {
                'correct': correct_pro,
                'incorrect': incorrect_pro,
            }
        }
    }

if __name__ == "__main__":
    def after_filtering(post_filtering_metrics):
        plot_sampling_frequencies(post_filtering_metrics['frequencies'])
        plot_ages(post_filtering_metrics['ages'])
        plot_widths(post_filtering_metrics['widths'])

    instance = parse_second_instance({ 'after_filtering': after_filtering })
    saccades = instance['saccades']
    plot_post_processing_trials(saccades, 'anti')
    plot_post_processing_trials(saccades, 'pro')
    plot_responses_times_distributions(saccades)
