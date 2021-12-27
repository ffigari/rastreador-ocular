import sys, os, json, shutil, math
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

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

        if n == 'seguimiento':
            for e in t['config']['stimulusPositions']:
                e['ts'] = date_iso_string_to_datetime(e['ts'])
events = sorted(events, key=lambda d: d['ts'])
for e in events:
    e['ts'] = date_iso_string_to_datetime(e['ts'])

SAMPLING_DELTA = timedelta(0, 0.1)
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

def uniformly_sample_experiment_gazes_and_follow_up_stimulus(e):
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
    return [sample_gaze_and_follow_up_stimulus(t) for t in e]

def uniformly_sample_trial_gazes(t):
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
    title = "Mapa de calor de miradas estimadas (trial {})".format(trial_number)
    if experiment_name == 'antisacadas':
        title += '\nExperimento de antisacadas'
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

def plot_experiment_context(ax, experiment, top_limit):
    experimentStartedAt = experiment[0]['startedAt']
    experimentEndedAt = experiment[-1]['endedAt']

    ax.set_xlim(0, distance_in_ms(experimentEndedAt, experimentStartedAt))
    for trial_number, t in enumerate(experiment):
        t_start = distance_in_ms(t['startedAt'], experimentStartedAt)
        duration = distance_in_ms(t['endedAt'], t['startedAt'])
        ax.add_patch(Rectangle((t_start, 0), duration, top_limit,
             edgecolor = 'black',
             facecolor = (trial_number % 2, (trial_number + 1) % 2, 0, 0.2),
             fill=True,
             lw=0.5))
    for decalibrationEvent in [
        e for e in events
        if e['name'] == 'decalibration-detected' \
            and experimentStartedAt <= e['ts'] <= experimentEndedAt
    ]:
        ax.axvline(
            distance_in_ms(decalibrationEvent['ts'], experimentStartedAt),
            linewidth=2,
            linestyle='--',
            color='red'
        )

    for calibrationStartedEvent in [
        e for e in events
        if e['name'] == 'calibration-started' \
            and experimentStartedAt <= e['ts'] <= experimentEndedAt
    ]:
        calibrationFinishedEvent = [
          e for e in events
          if e['name'] == 'calibration-finished' \
              and calibrationStartedEvent['ts'] <= e['ts'] <= experimentEndedAt
        ][0]
        t_start = distance_in_ms(calibrationStartedEvent['ts'], experimentStartedAt)
        duration = distance_in_ms(calibrationFinishedEvent['ts'], calibrationStartedEvent['ts'])
        ax.add_patch(Rectangle((t_start, 0), duration, top_limit,
             edgecolor = 'black',
             facecolor = (0, 0, 1, 0.2),
             fill=True,
             lw=0.5))

if os.path.isdir('output'):
    shutil.rmtree('output')
os.mkdir('output')

plt.rcParams['figure.figsize'] = [10, 7]
for n in experiments:
    e = experiments[n]

    for trial_number, t in enumerate(e):
        trial_estimated_gazes = uniformly_sample_trial_gazes(t)
        create_heatmap(n, trial_number, t, trial_estimated_gazes)

    if n == 'seguimiento':
        fig, ax = plt.subplots()
        seguimiento_data = []
        top_limit = 0
        for trial_samples in uniformly_sample_experiment_gazes_and_follow_up_stimulus(e):
            x_axis_distances = [
                abs(s['gaze_x'] - s['stimulus_x'])
                for s
                in trial_samples
            ]
            y_axis_distances = [
                abs(s['gaze_y'] - s['stimulus_y'])
                for s
                in trial_samples
            ]
            top_limit = max(top_limit, max(x_axis_distances), max(y_axis_distances))
            timestamps = [
                distance_in_ms(s['ts'], e[0]['startedAt'])
                for s
                in trial_samples
            ]
            seguimiento_data.append([x_axis_distances, y_axis_distances, timestamps])
        plot_experiment_context(ax, e, top_limit)
        for [x_axis_distances, y_axis_distances, timestamps] in seguimiento_data:
            ax.plot(
                timestamps, x_axis_distances,
                color="green", linewidth=0.5
            )
            ax.plot(
                timestamps, y_axis_distances,
                color="blue", linewidth=0.5
            )
        plt.savefig(
            'output/seguimiento-gaze_stimulus_distances'
        )
