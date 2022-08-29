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

def read_raw_experiment(path):
    with open(path, 'r') as f:
        jspsych_start_time = None
        rastoc_events = None

        csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
        headers = next(csv_rows_iterator, None)

        jspsych_start_time_idx = headers.index('jspsych_start_time')
        trial_type_idx = headers.index('trial_type')
        events_idx = headers.index('events')

        for row in csv_rows_iterator:
            v = row[jspsych_start_time_idx]
            if v != '':
                jspsych_start_time = v
                continue
            
            if row[trial_type_idx] == 'events-tracking-stop':
                rastoc_events = json.loads(row[events_idx])
                continue

        return jspsych_start_time, rastoc_events

import dateutil.parser
class Experiment:
    experiment_id = 0
    def __init__(self, experiment_path): 
        jspsych_start_ts_str, rastoc_events, gaze_estimations = \
            read_raw_experiment(experiment_path)

        calibrations_starts = []
        calibrations_ends = []
        decalibration_notifications = []
        jspsych_start_ts = dateutil.parser.isoparse(jspsych_start_ts_str)
        for e in rastoc_events:
            e_ts = dateutil.parser.isoparse(e['timestamp'])
            t = (e_ts - jspsych_start_ts).total_seconds() * 1000
            n = e['event_name']
            if n == 'rastoc:calibration-started':
                calibrations_starts.append(t)
            elif n == 'rastoc:calibration-succeeded':
                calibrations_ends.append(t)
            elif n == 'rastoc:decalibration-detected':
                decalibration_notifications.append(t)

        # TODO 
        gaze_estimations = ...


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
