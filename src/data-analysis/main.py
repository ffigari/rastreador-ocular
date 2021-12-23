import sys, os, json, shutil, math
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter

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
        t['relevantDataStartsAt'] = \
            date_iso_string_to_datetime(t['config']['relevantDataStartsAt']) \
            if 'relevantDataStartsAt' in t['config'] \
            else t['startedAt']
        t['relevantDataFinishesAt'] = \
            date_iso_string_to_datetime(t['config']['relevantDataFinishesAt']) \
            if 'relevantDataFinishesAt' in t['config'] \
            else t['endedAt']
events = sorted(events, key=lambda d: d['ts'])
for e in events:
    e['ts'] = date_iso_string_to_datetime(e['ts'])

def uniformly_sample_trial_gazes(t):
    trial_gaze_events = [
        e
        for e
        in events
        if e['name'] == 'gaze-estimation' \
            and t['relevantDataStartsAt'] <= e['ts'] <= t['relevantDataFinishesAt']
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

def create_heatmap(experiment_name, trial_number, trial, gazes):
    xs = [min(system_config['viewportWidth'], max(0, g['x'])) for g in gazes]
    ys = [min(system_config['viewportHeight'], max(0, g['y'])) for g in gazes]

    x_min = math.floor(min(xs))
    y_min = math.floor(min(ys))

    x_delta = math.ceil(max(xs)) - x_min
    y_delta = math.ceil(max(ys)) - y_min

    gaze_histogram, xedges, yedges = np.histogram2d(
        xs,
        ys,
        bins=(x_delta, y_delta)
    )

    heatmap = np.zeros((
        system_config['viewportWidth'],
        system_config['viewportHeight']
    ))
    heatmap[
        x_min:x_min + x_delta,
        y_min:y_min + y_delta,
    ] = gaze_histogram
    heatmap = gaussian_filter(heatmap, sigma=30)
    
    plt.clf()
    extent = [
        0, system_config['viewportWidth'], system_config['viewportHeight'], 0
    ]
    plt.imshow(heatmap.T, extent=extent, origin='upper')
    ax = plt.gca()
    title = "Mapa de calor de miradas estimadas"
    if experiment_name == 'antisacadas':
        title += '\nExperimento de antisacadas (trial {})'.format(trial_number)
        if trial['config']['isAntisaccadeTask']:
            title += ' - Tarea de antisacada'
        else:
            title += ' - Tarea de prosacada'
        title += '\nEstímulo mostrado a la '
        if trial['config']['targetAppearsInRightSide']:
            title += 'derecha'
        else:
            title += 'izquierda'
    ax.set_title(title, fontdict={ 'fontsize': 7 })
    plt.savefig(
        'output/{}-{}-intensity-heatmap'.format(experiment_name, trial_number)
    )


if os.path.isdir('output'):
    shutil.rmtree('output')
os.mkdir('output')
for n in experiments:
    for trial_number, t in enumerate(experiments[n]):
        create_heatmap(n, trial_number, t, uniformly_sample_trial_gazes(t))
