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
        e['pre_normalization_x'] = e['x']
        e['x'] = interpolate_between(e['x'], xa, ya, xb, yb)
    return trial

def normalize(ts):
    return [normalize_trial(t) for t in ts]
