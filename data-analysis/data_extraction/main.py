from data_extraction.instances.first import load_first_instance
from data_extraction.instances.second import load_second_instance

class Results():
    def __init__(self):
        fi = load_first_instance()
        si = load_second_instance()
        self.first_instance = fi
        self.second_instance = si

def load_results():
    return Results()


###

import os 
import csv
import json
import datetime

def iso_date_string_to_datetime(v):
    return dateutil.parser.isoparse(v)

def read_raw_experiment(path):
    with open(path, 'r') as f:
        jspsych_start_time = None
        rastoc_events = None
        raw_gaze_estimations = []

        csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
        headers = next(csv_rows_iterator, None)

        jspsych_start_time_idx = headers.index('jspsych_start_time')
        trial_type_idx = headers.index('trial_type')
        trial_start_ts_idx = headers.index('trial_start_ts')
        time_elapsed_idx = headers.index('time_elapsed')

        events_idx = headers.index('events')
        webgazer_data_idx = headers.index('webgazer_data')

        for row in csv_rows_iterator:
            v = row[jspsych_start_time_idx]
            if v != '':
                jspsych_start_time = iso_date_string_to_datetime(v)
                continue
            
            if row[trial_type_idx] == 'events-tracking-stop':
                rastoc_events = [{
                    'event_name': e['event_name'],
                    'ts': dateutil.parser.isoparse(e['timestamp'])
                } for e in json.loads(row[events_idx])]
                continue

            if row[webgazer_data_idx] != '' and row[trial_start_ts_idx] != '':
                trial_start_ts = \
                    iso_date_string_to_datetime(
                        json.loads(row[trial_start_ts_idx]))
                def convert(e):
                    return {
                        'x': e['x'],
                        'ts': trial_start_ts + datetime.timedelta(milliseconds=e['t'])
                    }
                raw_gaze_estimations.extend([
                    convert(e)
                    for e in json.loads(row[webgazer_data_idx])
                ])

        return jspsych_start_time, rastoc_events, raw_gaze_estimations

import dateutil.parser
class Experiment:
    experiment_id = 0
    def __init__(self, experiment_path): 
        jspsych_start_ts, rastoc_events, raw_gaze_estimations = \
            read_raw_experiment(experiment_path)

        calibrations_starts = []
        calibrations_ends = []
        validations_starts = []
        validations_ends = []
        decalibration_notifications = []
        for e in rastoc_events:
            n = e['event_name']

            if n == 'rastoc:calibration-started':
                calibrations_starts.append(e['ts'])
            elif n == 'rastoc:calibration-succeeded' or n == 'rastoc:calibration-failed':
                calibrations_ends.append(e['ts'])

            elif n == 'rastoc:validation-started':
                validations_starts.append(e['ts'])
            elif n == 'rastoc:validation-succeeded' or n == 'rastoc:validation-failed':
                validations_ends.append(e['ts'])

            elif n == 'rastoc:decalibration-detected':
                decalibration_notifications.append(e['ts'])

        gaze_estimation_blocks = []
        current_block_start = 0
        def close_block(i, current_block_start):
            gaze_estimation_blocks.append(
                raw_gaze_estimations[current_block_start:i+1])
            return i + 1
            
        es = raw_gaze_estimations
        INTRA_BLOCK_MAXIMUM_MS_BETWEEN_ESTIMATE = 100
        for i, e in enumerate(es):
            is_last_position = i+1 == len(es)
            next_estimation_is_far_away = False
            if not is_last_position:
                d_next = (es[i+1]['ts'] - e['ts']).total_seconds() * 1000
                next_estimation_is_far_away = \
                    d_next > INTRA_BLOCK_MAXIMUM_MS_BETWEEN_ESTIMATE;

            if is_last_position or next_estimation_is_far_away:
                current_block_start = close_block(i, current_block_start)
                continue

        print('start:', jspsych_start_ts)
        for b in gaze_estimation_blocks:
            print(b[0]['ts'], b[-1]['ts'])
        [print('calibration start:', ts) for ts in calibrations_starts]
        [print('calibration end:', ts) for ts in calibrations_ends]
        [print('validation start:', ts) for ts in validations_starts]
        [print('validation end:', ts) for ts in validations_ends]
        [print('decalibration:', ts) for ts in decalibration_notifications]


class EyeTrackedAnalysis:
    def __init__(self, experiments_path):
        if not os.path.isdir(experiments_path):
            raise Exception('Directory for experiment\'s data is not present. Expected path is `{}`.'.format(experiments_path))

        experiments_filenames = os.listdir(experiments_path)
        if len(experiments_filenames) == 0:
            raise Exception('No instances of the analysis were found at {}.'.format(experiments_path))

        self.first_experiment = Experiment(os.path.join(experiments_path, experiments_filenames[0]))

class SensitivityAnalysis(EyeTrackedAnalysis):
    def __init__(self):
        super().__init__('data-analysis/data_extraction/raw_data/sensitivity_analysis')
