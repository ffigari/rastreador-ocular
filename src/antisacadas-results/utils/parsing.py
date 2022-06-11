import os, re, csv, json

from utils.normalizer import Normalizer
from utils.trials_collection import TrialsCollection
from utils.sampling import uniformize_sampling

run_id_regex = re.compile('antisacadas_(\d{1,3}).csv')
data_path = 'src/antisacadas-results/data'

def parse_trials():
    parsed_trials = []
    counts_per_run = dict()
    for file_name in os.listdir(data_path):
        run_id = int(run_id_regex.match(file_name).group(1))
        counts_per_run[run_id] = dict()
        counts_per_run[run_id]['pro'] = dict()
        counts_per_run[run_id]['pro']['original_count'] = 0
        counts_per_run[run_id]['anti'] = dict()
        counts_per_run[run_id]['anti']['original_count'] = 0
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
                        'viewport_width': int(row[viewport_width_idx])
                    }
                    counts_per_run[run_id][parsed_trial['saccade_type']]['original_count'] += 1
    
                    # Normalize estimates
                    normalized_x_estimates = normalizer.normalize_estimates([
                        { 'x': e['x'], 't': e['t'] }
                        for e in original_estimates
                    ])
    
                    # Estimate will be mirrored so that we can assume that the trial
                    # visual cue was shown to the right in all trials
                    if parsed_trial['cue_was_shown_at_left']:
                        normalized_x_estimates = [
                            { 'x': -e['x'], 't': e['t'] }
                            for e in normalized_x_estimates
                        ]
    
                    # Uniformize sampling
                    interpolated_x_estimates = \
                        uniformize_sampling(normalized_x_estimates)
    
                    # Center time axis of estimations so that we can assume that t=0
                    # corresponds to when the visual cue appears
                    cue_start_in_ms = int(row[intra_end_idx])
                    centered_x_estimates = [
                        {
                            'x': e['x'],
                            't': e['t'] - cue_start_in_ms
                        }
                        for e in interpolated_x_estimates
                    ]
    
                    # Save trial
                    parsed_trial['estimates'] = centered_x_estimates
                    parsed_trials.append(parsed_trial)
    
                else:
                    pass
    
    return TrialsCollection(parsed_trials), counts_per_run
