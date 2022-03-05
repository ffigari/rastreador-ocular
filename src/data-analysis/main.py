import csv
import re
import os 
import json
import matplotlib.pyplot as plt

# Read trials results
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
        # TODO: Hay que saltarse los trials iniciales de prueba
        for row in csv_rows_iterator:
            if row[inner_width_idx] != '"':
                inner_width = json.loads(row[inner_width_idx])
            if row[exp_name_idx] == "antisaccade":
                run_trials.append({
                    "trial_id": json.loads(row[trial_id_idx]),
                    "gaze_estimations": json.loads(row[wg_data_idx]),
                    "center_x": json.loads(row[center_x_idx]),
                    "center_y": json.loads(row[center_y_idx]),
                    "cue_show_at_left": json.loads(row[cue_shown_at_left_idx]),
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

#fig, ax = plt.subplots()
#for trial in trials:
#    ax.plot(
#        [e['t'] for e in trial['gaze_estimations']],
#        [e['x'] for e in trial['gaze_estimations']],
#        alpha=0.4,
#        linewidth=0.7
#    )
#plt.show()

def normalize(trial):
    estimations = []
    for g in trial["gaze_estimations"]:
        # Center, normalize and mirror data
        # To prevent having to take into account the side in which the visual
        # cue is shown, we mirror the data when it gets shown in the left side.
        # Then the coordinate gets also centered and normalized so that we can
        # assume that on every trial and for every subject the coordinate in 
        # which the stimulus was shown is x = 1
        x = (
            -1 if trial['cue_show_at_left'] else 1
        ) * (g['x'] - trial['center_x']) / trial['cue_abs_x_delta']
        estimations.append({
            'x': x,
            't': g['t']
        })
    cue_t_start = \
        trial['pre_duration'] + \
        trial['fixation_duration'] + \
        trial['mid_duration']
    for e in estimations:
        e['t'] -= cue_t_start
    return {
        "run_id": trial["run_id"],
        "trial_id": trial["trial_id"],
        "estimations": estimations,
        "pre_start": - cue_t_start,
        "fixation_start": - cue_t_start + trial['pre_duration'],
        "mid_start": - cue_t_start + trial['pre_duration'] + trial['fixation_duration'],
        "cue_start": 0,
        "cue_finish": trial['cue_duration']
    }

def has_enough_mid_estimations(trial):
    return len([
        e for e in trial['estimations'] if trial['mid_start'] <= e['t'] <= trial['cue_start']
    ]) > 0

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

c = [normalize(t) for t in trials]
d = [separate_into_phases(t) for t in c if has_enough_mid_estimations(t)]
if len(c) - len(d):
    print(
        "%d trials out of %d were filtered out due to not having mid phase estimations" % (
            len(c) - len(d),
            len(c)
        )
    )
fig, ax = plt.subplots()
for t in d:
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
ax.axvline( 0, linestyle="--", color='black', alpha=0.3)
ax.axhline( 1, linestyle="--", color='black', alpha=0.3)
ax.axhline(-1, linestyle="--", color='black', alpha=0.3)
plt.show()
