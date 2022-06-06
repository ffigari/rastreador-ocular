from utils.parsing import parse_trials
from utils.cleaning import clean

trials, counts_per_run = parse_trials()
print('>> Original count: {:d} trials distributed in {:d} subjects'.format(
    trials.count, trials.runs_count
))

trials_post_processing, counts_per_run = clean(trials, counts_per_run)
print('>> Post processing count: {:d} trials distributed in {:d} subjects'.format(
    trials_post_processing.count, trials_post_processing.runs_count
))
