from utils.parsing import parse_trials
from utils.cleaning import clean
from main import drop_runs_without_enough
from utils.trials_collection import TrialsCollection
from common.plots import plot_sampling_frequencies
from common.plots import plot_ages
from common.plots import plot_widths

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

plot_sampling_frequencies(frequencies)
plot_ages(ages)
plot_widths(widths)

trials = TrialsCollection(kept_trials)
