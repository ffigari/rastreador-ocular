import sys, os
unwanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
wanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/second_instance'
if unwanted in sys.path:
    sys.path.remove(unwanted)
    sys.path = [wanted] + sys.path

from main import drop_runs_without_enough
from utils.parsing import parse_trials
from utils.cleaning import clean
from common.main import Instance
from common.main import Trial
from trials_response_times import compute_response_times_in_place
from incorrect_trials import divide_trials_by_correctness

class SecondTrial(Trial):
    def __init__(self, parsed_trial):
        super().__init__(parsed_trial['run_id'])

class SecondInstance(Instance):
    def load_data(self):
        pts, counts_per_run = parse_trials()
        return [SecondTrial(pt) for pt in pts]

    def build_tex_context(self):
        return {
            "second__starting_sample__trials_count": 'TODO',
            "second__starting_sample__subjects_count": 'TODO',
        }

def parse_second_instance(cbs):
    trials, counts_per_run = parse_trials()
    # starting_ts
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
    # outlier_ts, inlier_ts

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

def plot_second_post_processing_trials(saccades):
    plot_post_processing_trials(saccades['anti'], 'antisacadas')
    plot_post_processing_trials(saccades['pro'], 'prosacadas')

if __name__ == "__main__":
    def after_filtering(post_filtering_metrics):
        plot_sampling_frequencies(post_filtering_metrics['frequencies'])
        plot_ages(post_filtering_metrics['ages'])
        plot_widths(post_filtering_metrics['widths'])

    instance = parse_second_instance({ 'after_filtering': after_filtering })
    saccades = instance['saccades']
    plot_second_post_processing_trials(saccades)
    plot_responses_times_distributions(saccades)
