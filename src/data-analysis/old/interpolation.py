from time_utils import SAMPLING_DELTA 

def get_interpolator_for(xy_events):
    def interpolate_at(ts):
        if ts < xy_events[0]['ts']:
            raise Exception('Timestamp to interpolate is too small')
        if ts > xy_events[-1]['ts']:
            raise Exception('Timestamp to interpolate is too big')

        for (lower, upper) in zip(xy_events, xy_events[1:]):
            # search the enclosing events of the input timestamp
            if ts > upper['ts']:
                continue

            # handle edge cases
            if ts == lower['ts']:
                return lower
            if ts == upper['ts']:
                return upper

            # perform first order interpolation within the enclosing events
            def interpolate_for_axis(axis):
                ts_u_s = (upper['ts'] - lower['ts']).total_seconds()
                ts_s = (ts - lower['ts']).total_seconds()
                return \
                    lower[axis] + \
                    ts_s * (lower[axis] - upper[axis]) / (- ts_u_s)

            return {
                'ts': ts,
                'x': interpolate_for_axis('x'),
                'y': interpolate_for_axis('y'),
            }
    return interpolate_at

def uniformly_sample_experiment_gazes_and_follow_up_stimulus(events, experiment):
    def sample_gaze_and_follow_up_stimulus(t):
        trial_gaze_events = [
            e
            for e
            in events
            if e['name'] == 'gaze-estimation' \
                    and t['relevantDataStartsAt'] <= e['ts'] <= t['relevantDataFinishesAt']
        ]
        stimulus_events = [
            e for e in t['config']['stimulusPositions']
        ]
        gaze_interpolator = get_interpolator_for(trial_gaze_events)
        stimulus_interpolator = get_interpolator_for(stimulus_events)
        trial_interpolations = []
        ts = max(trial_gaze_events[0]['ts'], stimulus_events[0]['ts'])
        limit_ts = min(trial_gaze_events[-1]['ts'], stimulus_events[-1]['ts'])
        while ts <= limit_ts:
            gaze = gaze_interpolator(ts)
            stimulus = stimulus_interpolator(ts)
            trial_interpolations.append({
                'ts': ts,
                'gaze_x': gaze['x'],
                'gaze_y': gaze['y'],
                'stimulus_x': stimulus['x'],
                'stimulus_y': stimulus['y'],
            })
            ts = ts + SAMPLING_DELTA
        return trial_interpolations
    return [sample_gaze_and_follow_up_stimulus(t) for t in experiment]

def uniformly_sample_trial_gazes(events, t):
    trial_gaze_events = [
        e
        for e
        in events
        if e['name'] == 'gaze-estimation' \
            and t['relevantDataStartsAt'] <= e['ts'] <= t['relevantDataFinishesAt']
    ]
    interpolate_at = get_interpolator_for(trial_gaze_events)

    interpolated_gazes = []
    ts = trial_gaze_events[0]['ts']
    while ts <= trial_gaze_events[-1]['ts']:
        gaze = interpolate_at(ts)
        interpolated_gazes.append(gaze)
        ts = ts + SAMPLING_DELTA

    return interpolated_gazes

