import matplotlib.pyplot as plt

from utils.parsing import parse_trials
from utils.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
from utils.trials_collection import TrialsCollection
from fixated_trials import divide_trials_by_focus_on_center
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import divide_trials_by_early_saccade
from non_response_trials import divide_trials_by_non_response
from incorrect_trials import drop_incorrect_trials
from trials_response_times import compute_response_times_in_place

def plot_trials_by_run_and_saccade_type(trials):
    fig, axs = plt.subplots(ncols=2, nrows=trials.runs_count, sharex=True)
    for i, run_id in enumerate(trials.runs_ids):
        for j, saccade_type in enumerate(['pro', 'anti']):
            for t in trials.get_trials_by_run_by_saccade(run_id, saccade_type):
                es = t['estimates']
                axs[i][j].plot(
                    [e['t'] for e in es],
                    [e['x'] for e in es],
                    color="black",
                    alpha=0.3
                )
                axs[i][j].set_title("%ssaccades of run %d" % (
                    t['saccade_type'],
                    t['run_id']
                ))
                axs[i][j].axvline(
                    0,
                    linestyle="--",
                    color='black',
                    alpha=0.1,
                    label="apparition of visual cue"
                )
    plt.show()

def drop_and_report(fn, original_trials, filter_name):
    print(">> Applying '%s' filter" % filter_name)
    filtered_trials = fn(original_trials)
    print("%d trials (out of %d) were dropped" % (
        original_trials.count - filtered_trials.count,
        original_trials.count
    ))

    small_N_runs_ids = []
    for run_id in original_trials.runs_ids:
        run_filtered_pro_trials = \
            filtered_trials.get_trials_by_run_by_saccade(run_id, "pro")
        run_filtered_anti_trials = \
            filtered_trials.get_trials_by_run_by_saccade(run_id, "anti")
        pro_count_is_below_limit = \
            len(run_filtered_pro_trials) < MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
        anti_count_is_below_limit = \
            len(run_filtered_anti_trials) < MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
        if pro_count_is_below_limit or anti_count_is_below_limit:
            small_N_runs_ids.append(run_id)
    if len(small_N_runs_ids) > 0:
        print(
            "Dropping trials from runs whose trial count fell below limit (run_ids=[%s])" % ", ".join([str(run_id) for run_id in small_N_runs_ids]),
        )
        filtered_trials = TrialsCollection([
            t for t in filtered_trials.all()
            if t['run_id'] not in small_N_runs_ids
        ])

    return filtered_trials

saccade_types = ['pro', 'anti']
trials, counts_per_run = parse_trials()

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

runs_without_enough_valid_trials = []
print('>> Preprocessing drop count report')
print('---------------------------------------------------------------------------------------------------------------------------')
print('       || counts                                                                                        ||                 ')
print('run_id || original   || low frecuency | unfocused  | early saccade | non response || post preprocessing || is below minimum')
print('       || pro ~ anti || pro   ~ anti  | pro ~ anti | pro   ~ anti  | pro  ~ anti  || pro     ~ anti     ||                 ')
print('---------------------------------------------------------------------------------------------------------------------------')
for run_id, counts in sorted(
        counts_per_run.items(),
        key=lambda e: e[1]['pro']['post_preprocessing_count'] + e[1]['anti']['post_preprocessing_count']
    ):
    is_below_minimum = \
        counts['pro']['post_preprocessing_count'] < MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK or \
        counts['anti']['post_preprocessing_count'] < MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK

    if is_below_minimum:
        runs_without_enough_valid_trials.append(run_id)

    print('{:6d} || {:3d} ~ {:4d} || {:3d}   ~ {:4d}  | {:3d} ~ {:4d} | {:3d}   ~ {:4d}  | {:3d}   ~ {:4d} || {:3d}     ~ {:4d}     || {}'.format(
        run_id,
        counts['pro']['original_count'],
        counts['anti']['original_count'],
        counts['pro']['low_frequency_drop_count'],
        counts['anti']['low_frequency_drop_count'],
        counts['pro']['unfocused_drop_count'],
        counts['anti']['unfocused_drop_count'],
        counts['pro']['early_saccade_drop_count'],
        counts['anti']['early_saccade_drop_count'],
        counts['pro']['non_response_drop_count'],
        counts['anti']['non_response_drop_count'],
        counts['pro']['post_preprocessing_count'],
        counts['anti']['post_preprocessing_count'],
        is_below_minimum
    ))
print('---------------------------------------------------------------------------------------------------------------------------')

trials_of_runs_with_enough_trials = []

# TODO: Drop subjects with low amount of trials
# TODO: Keep incorrect trials
#       Their RT has to be reported
#       Besides, a detail of how many trials are dropped in each stage should be
#       accumulated
trials = drop_and_report(drop_incorrect_trials, trials, "incorrect trials")
plot_trials_by_run_and_saccade_type(trials)
compute_response_times_in_place(trials)

print('TODO: Report error rate')
print('TODO: Report mean RT for prosaccades')
print('TODO: Report mean RT for correct antisaccades')
print('TODO: Report mean RT for incorrect antisaccades')
print('TODO: Report mean ratio of incorrect antisaccades with a correction')
print('TODO: Report distributions of RT?')
