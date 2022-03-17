from constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from constants import TARGET_SAMPLING_PERIOD_IN_MS
from utils.interpolate import interpolate_between

def uniformize_trial_sampling(trial):
    t0 = trial['estimations'][0]['t']
    tn = trial['estimations'][-1]['t']

    def interpolate(t, axis):
        if t >= tn + TARGET_SAMPLING_PERIOD_IN_MS:
            raise Exception('input time is too big to interpolate')
        if t >= tn:
            return trial['estimations'][-1][axis]

        # find first bucket in which `t` is contained
        for i in range(1, len(trial['estimations'])):
            if trial['estimations'][i]['t'] > t:
                # this is the bucket since estimations are sorted by time
                past_estimation = trial['estimations'][i - 1]
                future_estimation = trial['estimations'][i]
                return interpolate_between(
                    t,
                    past_estimation['t'], past_estimation[axis],
                    future_estimation['t'], future_estimation[axis],
                )
        raise Exception('you should not be here')

    resampled_estimations = []
    t = t0
    while t < tn + TARGET_SAMPLING_PERIOD_IN_MS:
        resampled_estimations.append({
            'x': interpolate(t, 'x'),
            'y': interpolate(t, 'y'),
            't': t
        })
        t += TARGET_SAMPLING_PERIOD_IN_MS
    
    trial['estimations'] = resampled_estimations
    return trial

def uniformize_sampling(trials):
    return [uniformize_trial_sampling(t) for t in trials]

def tag_low_frecuency_trials(trials):
    low_frecuency_count = 0
    for t in trials:
        if t['original_sampling_frecuency_in_hz'] >= MINIMUM_SAMPLING_FREQUENCY_IN_HZ:
            continue
        low_frecuency_count += 1
        t['outlier'] = True
    if low_frecuency_count > 0:
        print(
            "%d trials out of %d were tagged as outliers due to low frecuency" % (
            low_frecuency_count,
            len(trials)
        ))
    return trials
