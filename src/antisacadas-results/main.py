import matplotlib.pyplot as plt

from utils.parsing import parse_trials
from utils.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
from utils.trials_collection import TrialsCollection
from fixated_trials import drop_non_fixated_trials
from saccade_detection import compute_saccades_in_place
from early_saccade_trials import drop_early_saccade_trials
from non_response_trials import drop_non_response_trials
from incorrect_trials import drop_incorrect_trials
from trials_response_times import compute_response_times_in_place

def plot_trials_by_run_and_saccade_type(trials):
    fig, axs = plt.subplots(ncols=2, nrows=trials.runs_count)
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

trials = parse_trials()
#plot_trials_by_run_and_saccade_type(trials)
trials = drop_and_report(drop_non_fixated_trials, trials, "non fixated")
compute_saccades_in_place(trials)
trials = drop_and_report(drop_early_saccade_trials, trials, "early saccade")
trials = drop_and_report(drop_non_response_trials, trials, "non respones")
trials = drop_and_report(drop_incorrect_trials, trials, "incorrect trials")
plot_trials_by_run_and_saccade_type(trials)
compute_response_times_in_place(trials)
