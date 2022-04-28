import os, re, csv, json
from normalizer import Normalizer

run_id_regex = re.compile('antisacadas_(\d{1,3}).csv')
data_path = 'src/antisacadas-results/data'

for file_name in os.listdir(data_path):
    run_id = int(run_id_regex.match(file_name).group(1))
    print('== %s ==' % file_name)
    with open(os.path.join(data_path, file_name), 'r') as f:
        csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
        headers = next(csv_rows_iterator, None)

        trial_index_idx = headers.index('trial_index')
        type_idx = headers.index('rastoc-type')
        center_x_idx = headers.index('center_x')
        stimulus_coordinate_idx = headers.index('stimulus-coordinate')
        validation_id_idx = headers.index('validation-id')
        validation_point_id_idx = headers.index('validation-point-id')
        validation_results_idx = headers.index('validation-results')
        validation_last_results_idx = headers.index('last-estimations')

        # Only coordinate x will be parsed and normalized since we don't need to
        # analyze vertical coordinate
        normalizer = None
        validations_count = 0

        while True:
            row = next(csv_rows_iterator, None)
            if row is None:
                break

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
                            int(row[center_x_idx]) + stimulus_delta,
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
            print(
                run_id,
                row[trial_index_idx]
            )
            # TODO: Parse trials
            #         - Estimations should be interpolated and normalized
            #         - Trials from the tutorial should not be included in the
            #           analysis but its validation must be considered
