from constants import POST_NORMALIZATION_FIXATION_TRESHOLD
from utils.interpolate import interpolate_between

def normalize_trial(trial):
    xs = [e['x'] for e in trial['estimations']]
    min_x = min(xs)
    max_x = max(xs)
    center = trial['run_estimated_center_mean']
    for e in trial['estimations']:
        xa, ya = None, None
        xb, yb = None, None
        if e['x'] < center:
            xa, ya = min_x, -1
            xb, yb = center, 0
        else:
            xa, ya = center, 0
            xb, yb = max_x, 1
        e['x'] = interpolate_between(e['x'], xa, ya, xb, yb)
    return trial

def normalize(ts):
    return [normalize_trial(t) for t in ts]

def tag_non_centered_trial(t):
    return t

def tag_non_centered(ts):
    count = 0
    for t in ts:
        xs = [
            e['x']
            for e
            in t['estimations']
            if t['fixation_start'] + 200 <= e['t'] <= t['mid_start']
        ]
        if max(
            abs(min(xs)), abs(max(xs))
        ) > POST_NORMALIZATION_FIXATION_TRESHOLD:
            count += 1
            t['outlier'] = True
    if count > 0:
        print(
            "%d trials out of %d were tagged as outliers due to not focusing the center during fixation phase" % (
            count,
            len(ts)
        ))
    return ts
