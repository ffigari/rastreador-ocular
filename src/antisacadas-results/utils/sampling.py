from utils.constants import TARGET_SAMPLING_PERIOD_IN_MS
from utils.interpolate import interpolate_with

def uniformize_sampling(es):
    t0 = es[0]['t']
    tn = es[-1]['t']

    def interpolate(t):
        if t >= tn + TARGET_SAMPLING_PERIOD_IN_MS:
            raise Exception('valor t muy alto')
        if t >= tn:
            return es[-1]['x']

        # find first bucket in which `t` is contained
        for i in range(1, len(es)):
            if es[i]['t'] > t:
                # this is the bucket since estimations are sorted by time
                past_estimation = es[i - 1]
                future_estimation = es[i]
                return interpolate_with(
                    t,
                    past_estimation['t'], past_estimation['x'],
                    future_estimation['t'], future_estimation['x']
                )
        raise Exception('you should not be here')

    resampled_estimations = []
    t = t0
    while t < tn + TARGET_SAMPLING_PERIOD_IN_MS:
        resampled_estimations.append({
            'x': interpolate(t),
            't': t
        })
        t += TARGET_SAMPLING_PERIOD_IN_MS

    return resampled_estimations
