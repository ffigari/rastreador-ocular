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
from common.plots import plot_sampling_frequencies
from common.plots import plot_ages
from common.plots import plot_widths
from common.plots import plot_post_processing_trials
from common.plots import plot_responses_times_distributions
from common.parsing import parse_parsing_callbacks

if modified:
    sys.path = sys_path_before

#####


#####


class Sample():
    def __init__(self, ts):
        self.trials_count = len(ts)
        self.subjects_count = len(list(set([t['run_id'] for t in ts])))

class FirstInstanceResults():
    def __init__(self):
        ts = mirror_trials(normalize(load_cleaned_up_trials()))
        self.starting_sample = Sample(ts)

        ts = drop_invalid_trials([t for t in ts if not t['outlier']])

# TODO: Volar este método
#       En particular no preocuparse en que siga andando
def parse_first_instance(cbs=None):
    cbs = parse_parsing_callbacks(cbs)

    trials_pre_processing
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
    print('>> Post minimum per run count: {:d} trials distributed in {:d} subjects'.format(
        len(trials_with_enough_per_run),
        len(list(set([t['run_id'] for t in trials_with_enough_per_run])))
    ))

    kept_trials, dropped_trials = [], []
    kept_runs_ids = []
    for t in trials:
        is_kept = len([
            te
            for te in trials_with_enough_per_run
            if te['run_id'] == t['run_id'] and te['trial_id'] == t['trial_id']
        ])
        if is_kept:
            kept_trials.append(t)
            kept_runs_ids.append(t['run_id'])
        else:
            dropped_trials.append(t)
    print('>> {:.2f} % of trials dropped; {:.2f} % of runs dropped'.format(
        100 * (len(dropped_trials) / len(trials)),
        100 * (
            (len(set([t['run_id'] for t in trials])) - len(set(kept_runs_ids))) \
            / len(set([t['run_id'] for t in trials]))
        )
    ))


    frequencies, ages, widths = [], [], []
    for kept, ts in [(True, kept_trials), (False, dropped_trials)]:
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

    compute_correcteness_in_place(kept_trials)
    trials = [t for t in kept_trials if t['subject_reacted']]
    correct_anti = [{
        'estimations': [{ 'x': e['x'], 't': e['t'] } for e in t['estimations']],
        'response_time': t['reaction_time'],
    } for t in trials if t['correct_reaction']]
    incorrect_anti = [{
        'estimations': [{ 'x': e['x'], 't': e['t'] } for e in t['estimations']],
        'response_time': t['reaction_time'],
    } for t in trials if not t['correct_reaction']]

    # TODO: Este ultimo objeto hay que guardarle el formato para poder reusar
    #       los gráficos
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
