from utils.main import load_cleaned_up_trials
from utils.normalize import normalize
from response_times import drop_invalid_trials
from response_times import mirror_trials
from common.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK

trials = mirror_trials(normalize(load_cleaned_up_trials()))
print('>> Original count: {:d} trials distributed in {:d} subjects'.format(
    len(trials), len(list(set([t['run_id'] for t in trials])))
))

trials_pre_processing = \
    drop_invalid_trials([t for t in trials if not t['outlier']])
print('>> Pre processing count: {:d} trials distributed in {:d} subjects'.format(
    len(trials_pre_processing),
    len(list(set([t['run_id'] for t in trials_pre_processing])))
))
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
