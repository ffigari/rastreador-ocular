import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from scipy.ndimage.filters import gaussian_filter

from time_utils import distance_in_ms 

plt.rcParams['figure.figsize'] = [10, 7]

def plot_experiment_context(events, ax, experiment, top_limit):
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

def plot_gaze_heatmap(system_config, experiment_name, trial_number, trial, gazes):
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

def plot_seguimiento(events, samples, experiment):
    fig, ax = plt.subplots()
    seguimiento_data = []
    top_limit = 0
    for trial_samples in samples:
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
            distance_in_ms(s['ts'], experiment[0]['startedAt'])
            for s
            in trial_samples
        ]
        seguimiento_data.append([x_axis_distances, y_axis_distances, timestamps])
    plot_experiment_context(events, ax, experiment, top_limit)
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
