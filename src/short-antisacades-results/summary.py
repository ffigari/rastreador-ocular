from utils.main import load_cleaned_up_trials
from utils.normalize import normalize
from response_times import drop_invalid_trials
from response_times import mirror_trials

trials = mirror_trials(normalize(load_cleaned_up_trials()))
print('>> Original count: {:d} trials distributed in {:d} subjects'.format(
    len(trials), len(list(set([t['run_id'] for t in trials])))
))

trials_post_processing = \
    drop_invalid_trials([t for t in trials if not t['outlier']])
print('>> Post processing count: {:d} trials distributed in {:d} subjects'.format(
    len(trials_post_processing),
    len(list(set([t['run_id'] for t in trials_post_processing])))
))
