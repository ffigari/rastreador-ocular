from utils.parsing import parse_trials
from utils.cleaning import clean
from main import drop_runs_without_enough

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
