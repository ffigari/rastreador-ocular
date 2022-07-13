from utils.constants import saccade_types
from sampling_frequencies import divide_trials_by_low_frequency
from fixated_trials import divide_trials_by_focus_on_center
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import divide_trials_by_early_saccade
from non_response_trials import divide_trials_by_non_response

def clean(trials, counts_per_run):
    # starting_ts
    trials, low_frequency_trials = divide_trials_by_low_frequency(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['low_frequency_drop_count'] = len([
                t for t in low_frequency_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    trials, unfocused_trials = divide_trials_by_focus_on_center(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['unfocused_drop_count'] = len([
                t for t in unfocused_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    compute_saccades_in_place(trials)

    trials, early_saccade_trials = divide_trials_by_early_saccade(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['early_saccade_drop_count'] = len([
                t for t in early_saccade_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    trials, non_response_trials = divide_trials_by_non_response(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['non_response_drop_count'] = len([
                t for t in non_response_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['post_preprocessing_count'] = \
                counts_per_run[run_id][st]['original_count'] - \
                counts_per_run[run_id][st]['low_frequency_drop_count'] - \
                counts_per_run[run_id][st]['unfocused_drop_count'] - \
                counts_per_run[run_id][st]['early_saccade_drop_count'] - \
                counts_per_run[run_id][st]['non_response_drop_count']

    return trials, counts_per_run
