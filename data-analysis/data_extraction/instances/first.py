import re, os, csv, json
from statistics import mean, stdev

from data_extraction.instance import Instance
from data_extraction.instance import PostProcessingMetrics
from data_extraction.trial import Trial
from data_extraction.trials_collection import TrialsCollection
from data_extraction.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from data_extraction.constants import TARGET_SAMPLING_PERIOD_IN_MS
from data_extraction.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
from data_extraction.interpolation import interpolate_between

POST_NORMALIZATION_FIXATION_TRESHOLD = 0.5
POST_NORMALIZATION_REACTION_TRESHOLD = 0.7
VISUAL_CUE_DURATION_IN_MS = 700
MINIMUM_TIME_FOR_SACCADE_IN_MS = 100

def compute_correcteness_in_place(trials):
    for t in trials:
        t.subject_reacted = False
        for e in t.estimations:
            if e['t'] < t.cue_start + MINIMUM_TIME_FOR_SACCADE_IN_MS:
                continue
            if abs(e['x']) < POST_NORMALIZATION_REACTION_TRESHOLD:
                continue
            t.subject_reacted = True
            t.response_time = e['t']
            t.correct_reaction = e['x'] < 0
            break

def estimates_are_centered(xs):
    return max(
        abs(min(xs)), abs(max(xs))
    ) <= POST_NORMALIZATION_FIXATION_TRESHOLD

def subject_did_not_focus_fixation_marker(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t.estimations
        if t.fixation_start + MINIMUM_TIME_FOR_SACCADE_IN_MS <= e['t'] <= t.mid_start
    ])

def subject_got_distracted(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t.estimations
        if t.mid_start <= e['t'] <= t.cue_start
    ])

def subject_reacted_too_quickly(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t.estimations
        if t.cue_start <= e['t'] <= t.cue_start + MINIMUM_TIME_FOR_SACCADE_IN_MS
    ])

def divide_trials(trials):
    non_centered_trials = []
    distracted_trials = []
    too_quick_trials = []
    valid_trials = []
    for t in trials:
        if subject_did_not_focus_fixation_marker(t):
            non_centered_trials.append(t)
        elif subject_got_distracted(t):
            distracted_trials.append(t)
        elif subject_reacted_too_quickly(t):
            too_quick_trials.append(t)
        else:
            valid_trials.append(t)
    return non_centered_trials, distracted_trials, too_quick_trials, valid_trials

def drop_invalid_trials(trials):
    return divide_trials(trials)[3]

class FirstTrial(Trial):
    def __init__(self, parsed_trial):
        super().__init__(
            parsed_trial['run_id'],
            parsed_trial['trial_id'],
            parsed_trial['original_sampling_frecuency_in_hz'],
            "anti",
            parsed_trial['estimations'],
            int(parsed_trial['subject_data']['edad']),
            parsed_trial['inner_width'],
            parsed_trial['run_center_x'],
            parsed_trial['run_estimated_center_mean']
        )
        self.is_outlier = parsed_trial['outlier']
        self.fixation_start = parsed_trial['fixation_start']
        self.mid_start = parsed_trial['mid_start']
        self.cue_start = parsed_trial['cue_start']

def group_by_run(trials):
    d = dict()
    for t in trials:
        r = t['run_id']
        if r not in d:
            d[r] = []
        d[r].append(t)
    return d

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


def tag_low_frecuency_trials(trials):
    low_frecuency_count = 0
    for t in trials:
        if t['original_sampling_frecuency_in_hz'] >= MINIMUM_SAMPLING_FREQUENCY_IN_HZ:
            continue
        low_frecuency_count += 1
        t['outlier'] = True
    return trials

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

def normalize_trial(trial):
    xs = [e['x'] for e in trial['estimations']]
    min_x = min(xs)
    max_x = max(xs)
    center = trial['run_estimated_center_mean']
    for e in trial['estimations']:
        xa, ya = None, None
        xb, yb = None, None
        if e['x'] < center:
            xa, ya = min_x, -1
            xb, yb = center, 0
        else:
            xa, ya = center, 0
            xb, yb = max_x, 1
        e['pre_normalization_x'] = e['x']
        e['x'] = interpolate_between(e['x'], xa, ya, xb, yb)
    return trial

def normalize(ts):
    return [normalize_trial(t) for t in ts]

def mirror_trial(t):
    for e in t['estimations']:
        e['pre_mirroring_x'] = e['x']
        if t['cue_shown_at_left']:
            e['x'] *= -1
    return t

def mirror_trials(trials):
    return [mirror_trial(t) for t in trials]

class FirstInstance(Instance):
    def __init__(self):
        super().__init__()

        self.correct_antisaccades_sample = self.correct_sample
        self.incorrect_antisaccades_sample = self.incorrect_sample
        self.corrected_antisaccades_sample = self.corrected_sample

    def _load_data(self):
        return [FirstTrial(t) for t in mirror_trials(normalize(load_cleaned_up_trials()))]

    def _process_starting_sample(self, ts):
        trials_pre_processing = drop_invalid_trials([
            t for t in ts.all() if not t.is_outlier
        ])

        count_per_run = dict()
        for t in trials_pre_processing:
            if t.run_id not in count_per_run:
                count_per_run[t.run_id] = 0
            count_per_run[t.run_id] += 1
        trials_with_enough_per_run = [
            t
            for t in trials_pre_processing
            if count_per_run[t.run_id] >= MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
        ]

        valid_ts, dropped_trials = [], []
        kept_runs_ids = []
        for t in ts.all():
            is_kept = len([
                te
                for te in trials_with_enough_per_run
                if te.run_id == t.run_id and te.trial_id == t.trial_id
            ])
            if is_kept:
                valid_ts.append(t)
                kept_runs_ids.append(t.run_id)
            else:
                dropped_trials.append(t)
        compute_correcteness_in_place(valid_ts)

        inlier_ts = [
            t for t in valid_ts
            if t.subject_reacted
        ]
        outlier_ts = [
            t for t in ts.all()
            if t.id not in set([t.id for t in inlier_ts])
        ]
        return TrialsCollection(outlier_ts), TrialsCollection(inlier_ts)

    def _look_for_response(self, inlier_ts):
        correct_ts = [
            t for t in inlier_ts.all()
            if t.subject_reacted and t.correct_reaction
        ]
        incorrect_ts = [
            t for t in inlier_ts.all()
            if t.subject_reacted and not t.correct_reaction
        ]
        return TrialsCollection(correct_ts), TrialsCollection(incorrect_ts)

    def _look_for_corrective_saccade(self, incorrect_ts):
        corrected_ts = []
        for t in incorrect_ts.all():
            for e in t.estimations:
                if e['t'] < t.response_time:
                    continue
                if e['x'] > - POST_NORMALIZATION_REACTION_TRESHOLD:
                    continue
                t.correction_time = e['t']
                corrected_ts.append(t)
                break
        return TrialsCollection(corrected_ts)

def load_first_instance():
    return FirstInstance()
