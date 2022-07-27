import os, re, csv, json
from statistics import mean

from constants import MINIMUM_TIME_FOR_SACCADE_IN_MS
from utils.normalizer import Normalizer
from utils.second_sampling import second_uniformize_sampling

run_id_regex = re.compile('antisacadas_(\d{1,3}).csv')
data_path = 'src/experimentation/second_instance/data'

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
