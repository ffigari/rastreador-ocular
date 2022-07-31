import re, os, csv, json
from statistics import mean

from data_extraction.instance import Instance
from data_extraction.sample import WithResponseSample
from data_extraction.sample import WithCorrectionSample
from data_extraction.trial import Trial
from data_extraction.trials_collection import TrialsCollection
from data_extraction.constants import TARGET_SAMPLING_PERIOD_IN_MS
from data_extraction.constants import MINIMUM_TIME_FOR_SACCADE_IN_MS
from data_extraction.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from data_extraction.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK

REQUIRED_FOCUS_TIME_PRE_VISUAL_CUE_IN_MS = 500
EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS = 100
saccade_types = ['pro', 'anti']

CUE = "cue_directed"
NON_CUE = "non_cue_directed"

def divide_trials_by_correctness(trials):
    correct_trials, incorrect_trials = [], []
    for t in trials.all():
        (i, j) = first_saccade_interval(t)
        saccade_x_start = t.estimations[i]['x']
        saccade_x_end = t.estimations[j]['x']
        saccade_direction = \
            CUE if saccade_x_start < saccade_x_end else NON_CUE

        expected_direction = \
            CUE if t.saccade_type == "pro" else NON_CUE

        if saccade_direction == expected_direction:
            correct_trials.append(t)
        else:
            incorrect_trials.append(t)

    return \
        TrialsCollection(correct_trials), \
        TrialsCollection(incorrect_trials)

def first_saccade_interval(t):
    return relevant_saccades(t)[0]

def second_saccade_interval(t):
    if len(relevant_saccades(t)) <= 1:
        return None
    return relevant_saccades(t)[1]

def compute_response_times_in_place(trials):
    for t in trials.all():
        (i, j) = first_saccade_interval(t)
        t.response_time = t.estimations[i]['t']

def drop_runs_without_enough(trials, counts_per_run):
    runs_without_enough_valid_trials = []
    for run_id, counts in sorted(
            counts_per_run.items(),
            key=lambda e: e[1]['pro']['post_preprocessing_count'] + e[1]['anti']['post_preprocessing_count']
        ):
        is_below_minimum = \
            counts['pro']['post_preprocessing_count'] < MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK or \
            counts['anti']['post_preprocessing_count'] < MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
    
        if is_below_minimum:
            runs_without_enough_valid_trials.append(run_id)
    
    if len(runs_without_enough_valid_trials) > 0:
        trials = TrialsCollection([
            t for t in trials.all()
            if t.run_id not in runs_without_enough_valid_trials
        ])
    return trials

def relevant_saccades(t):
    return [
        (i, j) for (i, j) in t.saccades_intervals
        if t.estimations[i]['t'] > EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
    ]

def divide_trials_by_low_frequency(trials):
    ok_trials, low_frequency_trials = [], []
    for t in trials.all():
        if t.original_sampling_frecuency_in_hz < MINIMUM_SAMPLING_FREQUENCY_IN_HZ:
            low_frequency_trials.append(t)
        else:
            ok_trials.append(t)


    return \
        TrialsCollection(ok_trials), \
        TrialsCollection(low_frequency_trials)

def divide_trials_by_focus_on_center(trials):
    focused_trials, unfocused_trials = [], []
    for t in trials.all():
        xs_before_visual_cue = [
            e['x'] for e in t.estimations
            if - REQUIRED_FOCUS_TIME_PRE_VISUAL_CUE_IN_MS < e['t'] < 0
        ]
        avg = sum(xs_before_visual_cue) / len(xs_before_visual_cue)
        if any([
            x - avg > 0.3 or abs(x) > 0.5
            for x in xs_before_visual_cue
        ]):
            unfocused_trials.append(t)
        else:
            focused_trials.append(t)

    return TrialsCollection(focused_trials), TrialsCollection(unfocused_trials)


def compute_saccades_in_place(trials):
    for t in trials.all():
        es = t.estimations
        velocities = [
            {
                't': es[i]['t'],
                'v': es[i + 1]['x'] - es[i]['x']
            } for i in range(len(es) - 1)
        ]

        saccades_intervals = []
        i = 0
        while i < len(velocities):
            j = i
            # first find contiguous intervals with same sign velocity...
            while \
                j + 1 < len(velocities) \
                and velocities[j + 1]['v'] * velocities[i]['v'] > 0:  # same sign?
                j += 1
            if j == i:
                i += 1
                continue

            # ...and then perform some checks
            interval_duration = es[j + 1]['t'] - es[i]['t']
            travelled_distance = abs(es[j + 1]['x'] - es[i]['x'])

            is_long_enough = interval_duration > 40
            travelled_enough_distance = travelled_distance > 0.6
            was_fast_enough = \
                travelled_distance / interval_duration > 0.15 / 100

            if is_long_enough and travelled_enough_distance and was_fast_enough:
                saccades_intervals.append((i, j + 1))
            i = j + 1

        t.saccades_intervals = saccades_intervals
        t.velocities = velocities

def divide_trials_by_early_saccade(trials):
    non_early_saccade_trials, early_saccade_trials = [], []
    for t in trials.all():
        es = t.estimations
        had_early_saccade = False
        for (i, j) in t.saccades_intervals:
            # we are cool with saccades that finished before the fixation period
            if es[j]['t'] < - REQUIRED_FOCUS_TIME_PRE_VISUAL_CUE_IN_MS:
                continue

            # but not with saccades that started during the fixation period or
            # too early after the visual cue appeareance
            if es[i]['t'] < EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS:
                had_early_saccade = True
            break
        
        if had_early_saccade:
            early_saccade_trials.append(t)
        else:
            non_early_saccade_trials.append(t)

    return \
        TrialsCollection(non_early_saccade_trials), \
        TrialsCollection(early_saccade_trials)

def divide_trials_by_non_response(trials):
    response_trials, non_response_trials = [], []
    for t in trials.all():
        if len(relevant_saccades(t)) > 0:
            response_trials.append(t)
        else:
            non_response_trials.append(t)

    return \
        TrialsCollection(response_trials), \
        TrialsCollection(non_response_trials)

def clean(trials, counts_per_run):
    # starting_ts
    trials, low_frequency_trials = divide_trials_by_low_frequency(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['low_frequency_drop_count'] = len([
                t for t in low_frequency_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    trials, unfocused_trials = divide_trials_by_focus_on_center(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['unfocused_drop_count'] = len([
                t for t in unfocused_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    compute_saccades_in_place(trials)

    trials, early_saccade_trials = divide_trials_by_early_saccade(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['early_saccade_drop_count'] = len([
                t for t in early_saccade_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    trials, non_response_trials = divide_trials_by_non_response(trials)
    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['non_response_drop_count'] = len([
                t for t in non_response_trials.get_trials_by_run_by_saccade(run_id, st)
            ])

    for run_id in counts_per_run.keys():
        for st in saccade_types:
            counts_per_run[run_id][st]['post_preprocessing_count'] = \
                counts_per_run[run_id][st]['original_count'] - \
                counts_per_run[run_id][st]['low_frequency_drop_count'] - \
                counts_per_run[run_id][st]['unfocused_drop_count'] - \
                counts_per_run[run_id][st]['early_saccade_drop_count'] - \
                counts_per_run[run_id][st]['non_response_drop_count']

    return trials, counts_per_run

class SecondTrial(Trial):
    def __init__(self, parsed_trial):
        super().__init__(
            parsed_trial['run_id'],
            parsed_trial['trial_id'],
            parsed_trial['original_frequency'],
            parsed_trial['saccade_type'],
            parsed_trial['estimates'],
            parsed_trial['age'],
            parsed_trial['viewport_width'],
            parsed_trial['run_center_x'],
            parsed_trial['run_estimated_center_mean'],
        )

def interpolate_with(x, xa, ya, xb, yb):
    # Here x and y are not used as the screen coordinates but as the
    # classic horizontal vs vertical axis.
    # Check https://en.wikipedia.org/wiki/Interpolation#Linear_interpolation
    return ya + (yb - ya) * (x - xa) / (xb - xa)

def second_uniformize_sampling(es):
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

class Normalizer:
    def __init__(self, stimulus_results, validation_was_successful):
        regions_of_interest = ['center', 'left', 'right']
        position_grouped_average_estimates = dict()
        validated_positions_real_x = dict()
        for p in regions_of_interest:
            position_grouped_average_estimates[p] = []
        for p in regions_of_interest:
            for r in [r for r in stimulus_results if r['position'] == p]:
                validated_positions_real_x[p] = r['real-stimulus-x']
                es = [e['x'] for e in r['last-estimates']]
                if len(es) == 0:
                    continue
                position_grouped_average_estimates[p].append(sum(es) / len(es))

        validated_positions_average_x_estimate = dict()
        for p in regions_of_interest:
            if len(position_grouped_average_estimates[p]) > 0:
                validated_positions_average_x_estimate[p] = \
                    sum(position_grouped_average_estimates[p]) / \
                    len(position_grouped_average_estimates[p])
            else:
                validated_positions_average_x_estimate[p] = \
                    validated_positions_real_x[p]

        self.center_mapping = (
            validated_positions_average_x_estimate['center'],
            0
        )
        self.left_mapping = (
            validated_positions_average_x_estimate['left'],
            -1
        )
        self.right_mapping = (
            validated_positions_average_x_estimate['right'],
            1
        )

        self.is_sketchy_normalizer = not validation_was_successful

    def normalize_estimates(self, raw_estimates):
        normalized_estimates = []
        for re in raw_estimates:
            rx = re['x']
            a = None
            b = None
            if rx < self.center_mapping[0]:
                a = self.left_mapping
                b = self.center_mapping
            else:
                a = self.center_mapping
                b = self.right_mapping
            normalized_estimates.append({
                'x': interpolate_with(rx, a[0], a[1], b[0], b[1]),
                't': re['t']
            })
        return normalized_estimates

run_id_regex = re.compile('antisacadas_(\d{1,3}).csv')
data_path = 'data-analysis/data_extraction/raw_data/second'

def parse_trials():
    parsed_trials = []
    counts_per_run = dict()
    for file_name in os.listdir(data_path):
        run_id = int(run_id_regex.match(file_name).group(1))
        if run_id == 56:
            continue
        counts_per_run[run_id] = dict()
        counts_per_run[run_id]['pro'] = dict()
        counts_per_run[run_id]['pro']['original_count'] = 0
        counts_per_run[run_id]['anti'] = dict()
        counts_per_run[run_id]['anti']['original_count'] = 0
        run_parsed_trials = []
        with open(os.path.join(data_path, file_name), 'r') as f:
            csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
            headers = next(csv_rows_iterator, None)
    
            trial_index_idx = headers.index('trial_index')
            type_idx = headers.index('rastoc-type')
            is_tutorial_idx = headers.index('isTutorial')
    
            center_x_idx = headers.index('center_x')
            stimulus_coordinate_idx = headers.index('stimulus-coordinate')
    
            validation_id_idx = headers.index('validation-id')
            validation_point_id_idx = headers.index('validation-point-id')
            validation_results_idx = headers.index('validation-results')
            validation_last_results_idx = headers.index('last-estimations')
    
            saccade_type_idx = headers.index('typeOfSaccade')
            webgazer_data_idx = headers.index('webgazer_data')
            iti_end_idx = headers.index('itiEnd')
            fix_end_idx = headers.index('fixEnd')
            intra_end_idx = headers.index('intraEnd')
            response_end_idx = headers.index('responseEnd')
            cue_was_shown_at_left_idx = headers.index('cueShownAtLeft')
            viewport_width_idx = headers.index('viewportWidth')
    
            # Only coordinate x will be parsed and normalized since we don't need to
            # analyze vertical coordinate
            normalizer = None
            validations_count = 0
    
            run_age = None
            while True:
                row = next(csv_rows_iterator, None)
                if row is None:
                    break

                if int(row[trial_index_idx]) == 1:
                    d = json.loads(row[headers.index('response')])
                    if 'age' in d:
                        run_age = int(d['age'])
                    continue
    
                # If a validation is found, consume its rows to update the
                # coordinates normalizer
                if row[type_idx] == 'validation-stimulus':
                    stimulus_results = []
                    validation_was_successful = None
                    while True:
                        stimulus_delta = \
                            json.loads(row[stimulus_coordinate_idx])['x']
                        stimulus_results.append({
                            'position': \
                                'center' if stimulus_delta == 0 else \
                                'left' if stimulus_delta < 0 else \
                                'right',
                            'real-stimulus-x': \
                                round(float(row[center_x_idx])) + stimulus_delta,
                            'last-estimates': \
                                json.loads(row[validation_last_results_idx])
                        })
                        # The last row concerning this validation contains its
                        # results
                        if int(row[validation_point_id_idx]) == 5:
                            validation_was_successful = json.loads(row[
                                validation_results_idx
                            ])['relativePositionsAreCorrect']
                        row = next(csv_rows_iterator, None)
                        if row[type_idx] != 'validation-stimulus':
                            normalizer = Normalizer(
                                stimulus_results,
                                validation_was_successful
                            )
                            break
    
                if row[saccade_type_idx] != '':
                    original_estimates = json.loads(row[webgazer_data_idx])
                    trial_duration_in_ms = int(row[response_end_idx])
                    if json.loads(row[is_tutorial_idx]):
                        continue
                    if run_age is None:
                        continue
                    parsed_trial = {
                        'run_id': run_id,
                        'trial_id': int(row[trial_index_idx]),
                        'age': run_age,
                        'saccade_type': \
                            'pro' if row[saccade_type_idx] == 'prosaccade' \
                            else 'anti',
                        'cue_was_shown_at_left': \
                            json.loads(row[cue_was_shown_at_left_idx]),
                        'original_frequency': \
                            len(original_estimates) / (trial_duration_in_ms / 1000),
                        'viewport_width': int(row[viewport_width_idx]),
                        'run_center_x': int(int(row[viewport_width_idx]) / 2)
                    }
                    counts_per_run[run_id][parsed_trial['saccade_type']]['original_count'] += 1

                    uniformized_estimates = \
                        second_uniformize_sampling(original_estimates)

                    iti_end = int(row[iti_end_idx])
                    fix_end = int(row[fix_end_idx])
                    parsed_trial['trial_estimated_center_mean'] = mean([
                        e['x']
                        for e in uniformized_estimates
                        if iti_end + MINIMUM_TIME_FOR_SACCADE_IN_MS <= e['t'] <= fix_end
                    ])

                    pre_normalization_xs = [
                        e['x'] for e in uniformized_estimates]
                    normalized_estimates = normalizer.normalize_estimates([
                        { 'x': e['x'], 't': e['t'] }
                        for e in original_estimates
                    ])

                    pre_mirroring_xs = [e['x'] for e in normalized_estimates]
                    if parsed_trial['cue_was_shown_at_left']:
                        normalized_estimates = [
                            { 'x': -e['x'], 't': e['t'] }
                            for e in normalized_estimates
                        ]
                    for i, e in enumerate(normalized_estimates):
                        e['pre_normalization_x'] = pre_normalization_xs[i]
                        e['pre_mirroring_x'] = pre_mirroring_xs[i]

                    cue_start_in_ms = int(row[intra_end_idx])
                    centered_x_estimates = [
                        {
                            'pre_normalization_x': e['pre_normalization_x'],
                            'pre_mirroring_x': e['pre_mirroring_x'],
                            'x': e['x'],
                            't': e['t'] - cue_start_in_ms
                        }
                        for e in normalized_estimates
                    ]
    
                    parsed_trial['estimates'] = centered_x_estimates
                    run_parsed_trials.append(parsed_trial)
                else:
                    pass

            if len(run_parsed_trials) > 0:
                run_estimated_center_mean = mean([
                    t['trial_estimated_center_mean']
                    for t in run_parsed_trials
                ])
                for t in run_parsed_trials:
                    t['run_estimated_center_mean'] = run_estimated_center_mean
                    parsed_trials.append(t)
    
    return parsed_trials, counts_per_run

class SecondInstance(Instance):
    def mean_incorrect_prosaccades_count_per_subject(self):
        return self.incorrect_prosaccades_sample.mean_trials_count_per_subject

    def prosaccades_correctness_percentage(self):
        cps__count = self.correct_prosaccades_sample.trials_count
        return cps__count / (cps__count + self.incorrect_prosaccades_sample.trials_count)

    def early_subjects_count(self):
        starting_ts = self.starting_sample.ts
        return len([
            run_id
            for run_id in starting_ts.runs_ids
            if starting_ts.get_trials_by_run(run_id).count() == 160
        ])

    def __init__(self):
        super().__init__()

        self.correct_prosaccades_sample = WithResponseSample(TrialsCollection([
            ct
            for ct in self.correct_sample.ts.all()
            if ct.saccade_type == "pro"
        ]))
        self.incorrect_prosaccades_sample = WithResponseSample(TrialsCollection([
            it
            for it in self.incorrect_sample.ts.all()
            if it.saccade_type == "pro"
        ]))

        self.correct_antisaccades_sample = WithResponseSample(TrialsCollection([
            ct
            for ct in self.correct_sample.ts.all()
            if ct.saccade_type == "anti"
        ]))
        self.incorrect_antisaccades_sample = WithResponseSample(TrialsCollection([
            it
            for it in self.incorrect_sample.ts.all()
            if it.saccade_type == "anti"
        ]))
        self.corrected_antisaccades_sample = WithCorrectionSample(TrialsCollection([
            ct
            for ct in self.corrected_sample.ts.all()
            if ct.id in set([
                iat.id
                for iat in self.incorrect_antisaccades_sample.ts.all()
            ])
        ]))

    def _load_data(self):
        pts, counts_per_run = parse_trials()
        self.counts_per_run = counts_per_run
        return [SecondTrial(pt) for pt in pts]

    def _process_starting_sample(self, starting_ts):
        trials_pre_processing, counts_per_run = clean(starting_ts, self.counts_per_run)
        trials_with_enough_per_run = drop_runs_without_enough(trials_pre_processing, counts_per_run)
        self.counts_per_run = counts_per_run

        kept_trials = []
        kept_runs_ids = []
        for t in starting_ts.all():
            is_kept = (t.run_id, t.trial_id) in set([
                (te.run_id, te.trial_id)
                for te in trials_with_enough_per_run.all()
            ])

            if is_kept:
                kept_trials.append(t)
                kept_runs_ids.append(t.run_id)

        inlier_ts = kept_trials
        outlier_ts = [
            t for t in starting_ts.all()
            if t.id not in set([t.id for t in inlier_ts])
        ]
        return TrialsCollection(outlier_ts), TrialsCollection(inlier_ts)

    def _look_for_response(self, inlier_ts):
        compute_response_times_in_place(inlier_ts)
        correct_ts, incorrect_ts = divide_trials_by_correctness(inlier_ts)

        return correct_ts, incorrect_ts

    def _look_for_corrective_saccade(self, incorrect_ts):
        corrected_ts = []
        for t in incorrect_ts.all():
            second_saccade_indexes = second_saccade_interval(t)
            second_saccade_was_detected = second_saccade_indexes is not None
            if second_saccade_was_detected:
                t.correction_time = t.estimations[second_saccade_indexes[0]]['t']
                corrected_ts.append(t)
            
        return TrialsCollection(corrected_ts)

def load_second_instance():
    return SecondInstance()
