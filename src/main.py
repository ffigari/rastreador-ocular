import sys
import numpy as np
import json
from functools import reduce
from datetime import datetime, timedelta
import math

def date_iso_string_to_datetime(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))

def distance_in_ms(oneDatetime, anotherDatetime):
    return (oneDatetime - anotherDatetime).total_seconds() * 1000


# Read file
if len(sys.argv) == 1:
    raise Exception(
        "Debe pasarse el primer path del output de JSPsych como primer parámetro."
    )
js_psych_output_file_path = sys.argv[1]
js_psych_output_file = open(js_psych_output_file_path)
js_psych_output = json.load(js_psych_output_file)
js_psych_output_file.close()

# Load data
system_config = None
experiments = {}
events = []
for entry in js_psych_output:
    if 'rastocCategory' not in entry:
        continue
    if entry['rastocCategory'] == 'system':
        system_config = entry['systemConfig']
        continue
    if entry['rastocCategory'] == 'trial-instance':
        name = entry['experiment']['name']
        if name not in experiments:
            experiments[name] = []
        experiments[name].append(entry['trial'])
    events.extend(entry['events'])

# Clean up data
for n in experiments:
    for t in experiments[n]:
        t['startedAt'] = date_iso_string_to_datetime(t['startedAt'])
        t['endedAt'] = date_iso_string_to_datetime(t['endedAt'])
events = sorted(events, key=lambda d: d['ts'])
for e in events:
    e['ts'] = date_iso_string_to_datetime(e['ts'])

def uniformly_sample_trial_gazes(t):
    trial_gaze_events = [
        e
        for e
        in events
        if e['name'] == 'gaze-estimation' \
           and t['startedAt'] <= e['ts'] <= t['endedAt']
    ]
    def interpolate_for(ts):
        if ts < trial_gaze_events[0]['ts']:
            raise Exception('Timestamp to interpolate is too small')
        if ts > trial_gaze_events[-1]['ts']:
            raise Exception('Timestamp to interpolate is too big')

        for (lower, upper) in zip(trial_gaze_events, trial_gaze_events[1:]):
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

    interpolated_gazes = []
    sampling_delta = timedelta(0, 0.1)
    ts = trial_gaze_events[0]['ts']
    while ts <= trial_gaze_events[-1]['ts']:
        gaze = interpolate_for(ts)
        interpolated_gazes.append(gaze)
        ts = ts + sampling_delta

    return interpolated_gazes

for n in experiments:
    for t in experiments[n]:
        gazes = uniformly_sample_trial_gazes(t)
        # TODO: Build heatmap of gaze intensity
