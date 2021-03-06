import os 
import json
import re
import csv
from statistics import mean, stdev

from common.constants import TARGET_SAMPLING_PERIOD_IN_MS
from constants import MINIMUM_TIME_FOR_SACCADE_IN_MS
from utils.sampling import tag_low_frecuency_trials
from utils.sampling import uniformize_sampling
from utils.normalize import normalize

run_id_regex = re.compile('short-antisaccades_(\d{1,3}).csv')
empty_hardware_regex = re.compile('(\{.*),"hardware":"(\})')
antisaccades_data_path = 'src/experimentation/first_instance/data'
internal_id = 0
def load_trials():
    trials = []
    for file_path in os.listdir(antisaccades_data_path):
        run_id = int(run_id_regex.match(file_path).group(1))
        with open(os.path.join(antisaccades_data_path, file_path), 'r') as f:
            csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
            headers = next(csv_rows_iterator, None)
    
            trial_id_idx = headers.index('trialId')
            trial_index_idx = headers.index('trial_index')
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
            response_idx = headers.index('response')
    
            run_trials = []
            inner_width = None
            i = 0
            subject_data = None
            for row in csv_rows_iterator:
                if row[inner_width_idx] != '"':
                    inner_width = json.loads(row[inner_width_idx])
                if json.loads(row[trial_index_idx]) == 2:
                    r = row[response_idx]
                    m = empty_hardware_regex.match(r)
                    if m is None:
                        subject_data = json.loads(r)
                    else:
                        subject_data = json.loads(m.group(1) + m.group(2))
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
                        # The following variable was incorrectly named when the
                        # experiment was set up
                        # Check line 47 of www/short-antisaccades.js
                        "cue_shown_at_left": not json.loads(row[cue_shown_at_left_idx]),
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
                estimations = trial['gaze_estimations']
                total_duration_in_ms = \
                    trial['pre_duration'] + \
                    trial['fixation_duration'] + \
                    trial['mid_duration'] + \
                    trial['cue_duration']
                global internal_id
                internal_id += 1
                formatted_trial = {
                    "id": internal_id,
                    "subject_data": subject_data,
                    "run_id": run_id,
                    "trial_id": trial["trial_id"],
                    "estimations": estimations,
                    "original_sampling_frecuency_in_hz": len(estimations) / (total_duration_in_ms / 1000),
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
                    "cue_abs_x_delta": trial["cue_abs_x_delta"],
                    "inner_width": inner_width,
                    "outlier": False  # This boolean will be modified as filters
                                      # are applied to indicate whether the
                                      # trial should be discarded
                }
                trials.append(formatted_trial)
    return trials

def group_by_run(trials):
    d = dict()
    for t in trials:
        r = t['run_id']
        if r not in d:
            d[r] = []
        d[r].append(t)
    return d

def center_trial_time_around_visual_cue_start(trial):
    cue_start = trial['cue_start']
    for e in trial['estimations']:
        e['t'] -= cue_start
    trial["pre_start"] -= cue_start
    trial["fixation_start"] -= cue_start
    trial["mid_start"] -= cue_start
    trial["cue_start"] -= cue_start
    trial["cue_finish"] -= cue_start
    return trial

def center_time_around_visual_cues_start(trials):
    return [center_trial_time_around_visual_cue_start(t) for t in trials]

# Kind of an ad-hoc function to filter trials with artifacts
def tag_artifacted_trials(trials):
    count = 0
    for t in trials:
        # Estimations should not go beyond 700ms since that's the amount of time
        # the visual cue is shown.
        # This assumes the data has already been centered around the visual cue. 
        too_many_estimations = t['estimations'][-1]['t'] > 800

        # Run 26 seems to be pure noise and 54 is pretty asymmetric
        is_noisy = t['run_id'] in [26, 54]

        if too_many_estimations or is_noisy:
            count += 1
            t['outlier'] = True
    return trials

def compute_deviation(all_trials):
    trials_by_run = group_by_run(all_trials)
    for run_id, trials in trials_by_run.items():
        center_x = trials[0]['center_x']
        for t in trials:
            if t['center_x'] != center_x:
                raise Exception(
                    'different center x values were found inside the same run (run_id={})'.format(run_id)
                )

        mean_fixations = []
        for t in trials:
            trial_mean_fixation_estimation = mean([
                e['x']
                for e
                in t['estimations']
                if t['fixation_start'] + MINIMUM_TIME_FOR_SACCADE_IN_MS <= e['t'] <= t['mid_start']
            ])
            t['mean_fixation_estimation'] = trial_mean_fixation_estimation
            mean_fixations.append(trial_mean_fixation_estimation)
        estimated_center_mean = mean(mean_fixations)

        center_deviation_factor = estimated_center_mean / center_x
        for t in trials:
            t['run_center_x'] = center_x
            t['run_estimated_center_mean'] = estimated_center_mean
            t['run_estimated_center_stdev'] = stdev(mean_fixations)
            t['run_deviation_factor'] = center_deviation_factor
    return all_trials

def load_cleaned_up_trials():
    return \
        compute_deviation(
        tag_artifacted_trials(
        center_time_around_visual_cues_start(
        uniformize_sampling(
        tag_low_frecuency_trials(
        load_trials())))))

def load_normalized_trials():
    return [
        t
        for t
        in normalize(load_cleaned_up_trials())
        if not t['outlier']
    ]
