import csv
import re
import os 
import json
import matplotlib.pyplot as plt
from statistics import mean, stdev

MINIMUM_SAMPLING_FREQUENCY_IN_HZ = 15
TARGET_SAMPLING_FREQUENCY_IN_HZ = 25
TARGET_SAMPLING_PERIOD_IN_MS = 1000 * (1 / TARGET_SAMPLING_FREQUENCY_IN_HZ)
SHOW_STUFF = True

def plot_x_coordinate_in_function_of_time(ax, trials, already_mirrored=True):
    for t in trials:
        for (phase, color) in [
            ('pre_estimations', 'red'),
            ('fixation_estimations', 'green'),
            ('mid_estimations', 'blue'),
            ('cue_estimations', 'black'),
        ]:
            ax.plot(
                [e['t'] for e in t[phase]],
                [e['x'] for e in t[phase]],
                alpha=0.4,
                linewidth=0.3,
                color=color,
            )
    ax.axvline(
        0,
        linestyle="--",
        color='black',
        alpha=0.3,
        label="apparition of visual cue"
    )
    ax.axhline(
        1,
        linestyle="--",
        color='red',
        alpha=0.3,
        label='position of visual cue' if already_mirrored else 'position of right visual cue'
    )
    if not already_mirrored:
        ax.axhline(
            -1,
            linestyle="--",
            color='blue',
            alpha=0.3,
            label='position of left visual cue'
        )
    ax.set_xlabel('time (in ms)')
    ax.set_ylabel('x coordinate of estimation')
    ax.set_title("evolution of estimation's x coordinate")
    ax.legend(loc='upper left')

antisaccades_data_path = 'src/data-analysis/short-antisaccades'
trials = []
for file_path in os.listdir(antisaccades_data_path):
    p = re.compile('short-antisaccades_(\d{1,3}).csv')
    run_id = p.match(file_path).group(1)
    with open(os.path.join(antisaccades_data_path, file_path), 'r') as f:
        csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
        headers = next(csv_rows_iterator, None)

        trial_id_idx = headers.index('trialId')
        inner_width_idx = headers.index('inner_width')
        wg_data_idx = headers.index('webgazer_data')
        exp_name_idx = headers.index('experimentName')
        center_x_idx = headers.index('center_x')
        center_y_idx = headers.index('center_y')
        cue_x_delta_idx = headers.index('cueXDistance')
        cue_shown_at_left_idx = headers.index('cueWasShownAtLeft')
        pre_trial_duration_idx = headers.index('intraTrialBlankDuration')
        fixation_duration_idx = headers.index('fixationDuration')
        mid_blank_duration_idx = headers.index('interTrialBlankDuration')
        cue_duration_idx = headers.index('cueDuration')

        run_trials = []
        inner_width = None
        i = 0
        for row in csv_rows_iterator:
            if row[inner_width_idx] != '"':
                inner_width = json.loads(row[inner_width_idx])
            if row[exp_name_idx] == "antisaccade":
                i += 1
                if i < 10:
                    # skip 10 first trials which are training trials
                    continue

                run_trials.append({
                    "trial_id": json.loads(row[trial_id_idx]),
                    "gaze_estimations": json.loads(row[wg_data_idx]),
                    "center_x": json.loads(row[center_x_idx]),
                    "center_y": json.loads(row[center_y_idx]),
                    "cue_shown_at_left": json.loads(row[cue_shown_at_left_idx]),
                    "cue_abs_x_delta": abs(json.loads(row[cue_x_delta_idx])),
                    "pre_duration": json.loads(row[pre_trial_duration_idx]),
                    "fixation_duration": json.loads(row[fixation_duration_idx]),
                    "mid_duration": json.loads(row[mid_blank_duration_idx]),
                    "cue_duration": json.loads(row[cue_duration_idx])
                })
        if inner_width is None:
            raise Exception(
                "Viewport inner width not found for run %d" % run_id
            )
        for trial in run_trials:
            trial['run_id'] = run_id
            trial['inner_width'] = inner_width
        trials.extend(run_trials)

def format(trial):
    estimations = trial['gaze_estimations']
    total_duration_in_ms = \
        trial['pre_duration'] + \
        trial['fixation_duration'] + \
        trial['mid_duration'] + \
        trial['cue_duration']
    return {
        "run_id": trial["run_id"],
        "trial_id": trial["trial_id"],
        "estimations": estimations,
        "sampling_frequency": len(estimations) / (total_duration_in_ms / 1000),
        "center_x": trial["center_x"],

        "pre_start": 0,
        "fixation_start": trial['pre_duration'],
        "mid_start": \
            trial['pre_duration'] + \
            trial['fixation_duration'],
        "cue_start": \
            trial['pre_duration'] + \
            trial['fixation_duration'] + \
            trial['mid_duration'],
        "cue_finish": total_duration_in_ms,

        "cue_shown_at_left": trial["cue_shown_at_left"],
        "cue_abs_x_delta": trial["cue_abs_x_delta"]
    }
trials = [format(t) for t in trials]

# Compute and filter by sampling frequency
frequencies_grouped_per_run = {}
for t in trials:
    if t['run_id'] not in frequencies_grouped_per_run:
        frequencies_grouped_per_run[t['run_id']] = []
    frequencies_grouped_per_run[t['run_id']].append(t['sampling_frequency'])
frequencies_per_run = {}
for k, v in frequencies_grouped_per_run.items():
    frequencies_per_run[k] = {
        'mean': mean(v),
        'std': stdev(v)
    }
    
if SHOW_STUFF:
    fig, ax = plt.subplots()
    ax.hist(
        [v['mean'] for _, v in frequencies_per_run.items()],
        ec="black"
    )
    ax.axvline(
        MINIMUM_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='red',
        alpha=0.3,
        label="minimum sampling frequency"
    )
    ax.axvline(
        TARGET_SAMPLING_FREQUENCY_IN_HZ,
        linestyle="--",
        color='black',
        alpha=0.3,
        label="target sampling frequency"
    )
    ax.legend()
    ax.set_xlabel('frequency (in Hz)')
    ax.set_ylabel('amount of runs')
    ax.set_title("Mean sampling frequency grouped by run")
    print('\n== sampling frequency')
    print('run id | mean | stdev')
    for k, v in frequencies_per_run.items():
        print("%d | %f | %f" % (int(k), v['mean'], v['std']))
    print('==')
    print('mean | %f | %f' % (
        mean([v['mean'] for k, v in frequencies_per_run.items()]),
        mean([v['std'] for k, v in frequencies_per_run.items()])
    ))
    print('====')
    plt.show()

ids_of_runs_without_enough_frequency = [
    k
    for k, v
    in frequencies_per_run.items()
    if v['mean'] < MINIMUM_SAMPLING_FREQUENCY_IN_HZ
]
previous_len = len(trials)
trials = [
    t
    for t
    in trials
    if t['run_id'] not in ids_of_runs_without_enough_frequency
]
dropped_count = previous_len - len(trials)
if dropped_count > 0:
    print(
        "trials from %d runs (%d trials out of %d) were dropped due to not having enough sampling frequency (minimum of %d Hz)" % (
            len(ids_of_runs_without_enough_frequency),
            dropped_count,
            previous_len,
            MINIMUM_SAMPLING_FREQUENCY_IN_HZ
        )
    )

def pre_estimations(trial):
    return [
        e for e in trial['estimations'] if trial['pre_start'] <= e['t'] <= trial['fixation_start']
    ]
def fixation_estimations(trial):
    return [
        e for e in trial['estimations'] if trial['fixation_start'] <= e['t'] <= trial['mid_start']
    ]
def mid_estimations(trial):
    return [
        e for e in trial['estimations'] if trial['mid_start'] <= e['t'] <= trial['cue_start']
    ]
def cue_estimations(trial):
    return [
        e for e in trial['estimations'] if trial['cue_start'] <= e['t'] <= trial['cue_finish']
    ]
def has_enough_estimations(trial):
    return \
        len(pre_estimations(trial)) > 0 and \
        len(fixation_estimations(trial)) > 0 and \
        len(mid_estimations(trial)) > 0 and \
        len(cue_estimations(trial)) > 0

d = [t for t in trials if has_enough_estimations(t)]
if len(trials) - len(d):
    print(
        "%d trials out of %d were filtered out due to not having enough estimations" % (
            len(trials) - len(d),
            len(trials)
        )
    )
trials = d

def normalize(trial):
    estimations = []
    for g in trial["estimations"]:
        # Center and normalize x coordinate so that we can assume that on every
        # trial and for every subject the coordinate in which the stimulus was
        # shown is x = 1 or x = -1
        x = (g['x'] - trial['center_x']) / trial['cue_abs_x_delta']
        estimations.append({
            'x': x,
            # i'm leavin `y` unchanged since atm it's not used later on
            'y': g['y'],
            't': g['t']
        })
    trial['estimations'] = estimations

    # Shift time values so that all trials are aligned at the start of the 
    # visual cuet
    cue_start = trial['cue_start']
    for e in trial['estimations']:
        e['t'] -= cue_start
    trial["pre_start"] -= cue_start
    trial["fixation_start"] -= cue_start
    trial["mid_start"] -= cue_start
    trial["cue_start"] -= cue_start
    trial["cue_finish"] -= cue_start
    return trial
trials = [normalize(t) for t in trials]
print('data normalized')

def uniformize_sampling(trial):
    t0 = trial['estimations'][0]['t']
    tn = trial['estimations'][-1]['t']

    def interpolate_between(x, xa, ya, xb, yb):
        # Here x and y are not used as the screen coordinates but as the
        # classic horizontal vs vertical axis.
        # Check https://en.wikipedia.org/wiki/Interpolation#Linear_interpolation
        if not xa <= x <= xb:
            raise Exception('can not interpolate outside of input points')
        return ya + (yb - ya) * (x - xa) / (xb - xa)

    def interpolate(t, axis):
        if t >= tn + TARGET_SAMPLING_PERIOD_IN_MS:
            raise Exception('input time is too big to interpolate')
        if t >= tn:
            return trial['estimations'][-1][axis]

        # find first bucket in which `t` is contained
        for i in range(1, len(trial['estimations'])):
            if trial['estimations'][i]['t'] > t:
                past_estimation = trial['estimations'][i - 1]
                # at this point `t < tn` so i != len(estimations)
                future_estimation = trial['estimations'][i]
                # this is the bucket since estimations are sorted by time
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
trials = [uniformize_sampling(t) for t in trials]
print('sampling rate frequency uniformized to %d Hz' % TARGET_SAMPLING_FREQUENCY_IN_HZ)

def separate_into_phases(trial):
    trial['pre_estimations'] = [
        e for e in trial['estimations'] if trial['pre_start'] <= e['t'] <= trial['fixation_start']
    ]
    trial['fixation_estimations'] = [
        e for e in trial['estimations'] if trial['fixation_start'] <= e['t'] <= trial['mid_start']
    ]
    trial['mid_estimations'] = [
        e for e in trial['estimations'] if trial['mid_start'] <= e['t'] <= trial['cue_start']
    ]
    trial['cue_estimations'] = [
        e for e in trial['estimations'] if trial['cue_start'] <= e['t'] <= trial['cue_finish']
    ]
    trial['pre_estimations'].append(trial['fixation_estimations'][0])
    trial['fixation_estimations'].append(trial['mid_estimations'][0])
    trial['mid_estimations'].append(trial['cue_estimations'][0])
    return trial
trials = [separate_into_phases(t) for t in trials]

if SHOW_STUFF:
    fix, ax = plt.subplots()
    plot_x_coordinate_in_function_of_time(ax, trials, already_mirrored=False)
    ax.set_title("normalized data")
    plt.show()

def run_is_symmetrical(trials):
    mean_mean_x = 0
    for t in trials:
        mean_x = 0
        for e in t['estimations']:
            mean_x += e['x']
        mean_x = mean_x / len(t['estimations'])
        mean_mean_x += mean_x
    mean_mean_x = mean_mean_x / len(trials)
    return abs(mean_mean_x) < 0.3

trials_per_run = {}
for t in trials:
    if t['run_id'] not in trials_per_run:
        trials_per_run[t['run_id']] = []
    trials_per_run[t['run_id']].append(t)
asymmetrical_runs_count = 0
for _, run_trials in trials_per_run.items():
    is_symmetrical = run_is_symmetrical(run_trials)
    if not is_symmetrical:
        asymmetrical_runs_count += 1
    for t in run_trials:
        t['belongs_to_symmetric_run'] = is_symmetrical

symmetrical_trials = [t for t in trials if t['belongs_to_symmetric_run']]
asymmetrical_trials = [t for t in trials if not t['belongs_to_symmetric_run']]
if SHOW_STUFF:
    fig, axs = plt.subplots(ncols=1, nrows=2)
    plot_x_coordinate_in_function_of_time(axs[0], symmetrical_trials, already_mirrored=False)
    axs[0].set_title("symmetrical runs' trials")
    plot_x_coordinate_in_function_of_time(axs[1], asymmetrical_trials, already_mirrored=False)
    axs[1].set_title("asymmetrical runs' trials")
    fig.subplots_adjust(hspace = 0.5)
    plt.show()
if len(asymmetrical_trials) > 0:
    print(
        "trials from %d runs (in total %d out of %d) were filtered out due to belonging to asymmetrical runs" % (
            asymmetrical_runs_count,
            len(asymmetrical_trials),
            len(asymmetrical_trials) + len(symmetrical_trials)
        )
    )
trials = symmetrical_trials

def mirror(trial):
    for e in trial['estimations']:
        # Mirror data so that we can assume the stimulus was shown at x = 1
        e['x'] = (
            -1 if trial['cue_shown_at_left'] else 1
        ) * e['x']
    return trial

if SHOW_STUFF:
    fig, axs = plt.subplots(ncols=1, nrows=2)
    plot_x_coordinate_in_function_of_time(axs[0], trials, already_mirrored=False)
    axs[0].set_title("non mirrored data")
trials = [mirror(t) for t in trials]
if SHOW_STUFF:
    plot_x_coordinate_in_function_of_time(axs[1], trials)
    axs[1].set_title("mirrored data")
    plt.show()

def fixation_marker_is_focused(trial):
    x_after_saccade_time = [
        abs(e['x'])
        for e
        in trial['fixation_estimations']
        if trial['fixation_start'] + 200 <= e['t'] <= trial['mid_start']
    ]
    avg_x = sum(x_after_saccade_time) / len(x_after_saccade_time)
    return avg_x < 0.4
for t in trials:
    t['fixation_marker_was_focused'] = fixation_marker_is_focused(t)

fixation_focused_trials = [
    t for t in trials if t['fixation_marker_was_focused']
]
fixation_non_focused_trials = [
    t for t in trials if not t['fixation_marker_was_focused']
]
fig, axs = plt.subplots(ncols=1, nrows=2)
plot_x_coordinate_in_function_of_time(axs[0], fixation_focused_trials)
axs[0].set_title("fixation was focused")
plot_x_coordinate_in_function_of_time(axs[1], fixation_non_focused_trials)
axs[1].set_title("fixation was not focused")
plt.show()
trials = fixation_focused_trials
