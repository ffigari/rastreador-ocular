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
        type_idx = headers.index('type')
        center_x_idx = headers.index('center_x')
        results_idx = headers.index('results')
        validation_succeded_idx = headers.index('validationSucceded')

        # Only coordinate x will be parsed and normalized since we don't need to
        # analyze vertical coordinate
        normalizer = None
        validations_count = 0
        for row in csv_rows_iterator:
            if (row[type_idx] != ''):
                center_x = int(row[center_x_idx])
                results = json.loads(row[results_idx])
                ui_validation_succeded = row[validation_succeded_idx]
                print('\n%d-th validation (ui success? %s)' % (
                    validations_count,
                    ui_validation_succeded
                ))
                normalizer = Normalizer(center_x, results)
                validations_count += 1
