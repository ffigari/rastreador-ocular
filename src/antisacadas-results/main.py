import matplotlib.pyplot as plt

from utils.parsing import parse_trials
from utils.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
from utils.trials_collection import TrialsCollection
from fixated_trials import divide_trials_by_focus_on_center
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import divide_trials_by_early_saccade
from non_response_trials import divide_trials_by_non_response
from incorrect_trials import divide_trials_by_correctness
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
print('>> Preprocessing drop count report:')
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

if len(runs_without_enough_valid_trials) > 0:
    print('>> Trials of {:d} runs (ids=[{:s}]) were dropped due to having less than {:d} trials per task after preprocessing'.format(
        len(runs_without_enough_valid_trials),
        ', '.join([str(i) for i in runs_without_enough_valid_trials]),
        MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
    ))
    trials = TrialsCollection([
        t for t in trials.all()
        if t['run_id'] not in runs_without_enough_valid_trials
    ])

compute_response_times_in_place(trials)
correct_trials, incorrect_trials = divide_trials_by_correctness(trials)
#plot_trials_by_run_and_saccade_type(correct_trials)
#plot_trials_by_run_and_saccade_type(incorrect_trials)

trials_per_correctness = dict()
for run_id in trials.runs_ids:
    trials_per_correctness[run_id] = dict()
    for st in saccade_types:
        trials_per_correctness[run_id][st] = {
            'correct': TrialsCollection(
                correct_trials.get_trials_by_run_by_saccade(run_id, st)),
            'incorrect': TrialsCollection(
                incorrect_trials.get_trials_by_run_by_saccade(run_id, st)),
        }

print('>> Correctness report:')
print('--------------------------------------------------------')
print('run id || # correct   | # incorrect  | correctness ratio')
print('       || pro  ~ anti | pro  ~ anti  | pro     ~ anti   ')
print('--------------------------------------------------------')
for run_id in trials.runs_ids:
    print('{:6d} || {:4d} ~ {:4d} | {:4d} ~ {:4d}  | {:1.2f}    ~ {:1.2f}   '.format(
        run_id,
        trials_per_correctness[run_id]['pro']['correct'].count,
        trials_per_correctness[run_id]['anti']['correct'].count,
        trials_per_correctness[run_id]['pro']['incorrect'].count,
        trials_per_correctness[run_id]['anti']['incorrect'].count,
        trials_per_correctness[run_id]['pro']['correct'].count / (
            trials_per_correctness[run_id]['pro']['correct'].count + \
            trials_per_correctness[run_id]['pro']['incorrect'].count),
        trials_per_correctness[run_id]['anti']['correct'].count / (
            trials_per_correctness[run_id]['anti']['correct'].count + \
            trials_per_correctness[run_id]['anti']['incorrect'].count)
    ))
print('--------------------------------------------------------')
total_pro_correct_count = sum([
    trials_per_correctness[run_id]['pro']['correct'].count
    for run_id in trials.runs_ids
])
total_anti_correct_count = sum([
    trials_per_correctness[run_id]['anti']['correct'].count
    for run_id in trials.runs_ids
])
total_pro_incorrect_count = sum([
    trials_per_correctness[run_id]['pro']['incorrect'].count
    for run_id in trials.runs_ids
])
total_anti_incorrect_count = sum([
    trials_per_correctness[run_id]['anti']['incorrect'].count
    for run_id in trials.runs_ids
])
print(' total || {:4d} ~ {:4d} | {:4d} ~ {:4d}  | {:1.2f}    ~ {:1.2f}   '.format(
    total_pro_correct_count,
    total_anti_correct_count,
    total_pro_incorrect_count,
    total_anti_incorrect_count,
    total_pro_correct_count / (total_pro_correct_count + total_pro_incorrect_count),
    total_anti_correct_count / (total_anti_correct_count + total_anti_incorrect_count)
))
print('--------------------------------------------------------')

print('>> Mean response time report:')
print('TODO: Report mean RT for prosaccades')
print('TODO: Report mean RT for correct antisaccades')
print('TODO: Report mean RT for incorrect antisaccades')

print('TODO: Report distributions of RT?')

print('TODO: For incorrect antisaccades, compute RT of correction if it exists')
print('TODO: Report mean ratio of incorrect antisaccades with a correction')
