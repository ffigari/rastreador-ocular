import numpy as np
import json
from functools import reduce
from datetime import datetime
import math

def parse_iso_date_string(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))

def distance_in_ms(oneDatetime, anotherDatetime):
    return (oneDatetime - anotherDatetime).total_seconds() * 1000

js_psych_output_file_path = "antisaccades-experiment.json"
js_psych_output_file = open(js_psych_output_file_path)
js_psych_output = json.load(js_psych_output_file)
js_psych_output_file.close()

class AntisaccadesTaskOutput:
    def __init__(self, estimations, started_at, ended_at, decalibration_detected):
        # TODO: Iterate over array and conver date strings to datetime objects
        self.estimations = estimations
        self.decalibration_detected = decalibration_detected

        self.started_at = parse_iso_date_string(started_at)
        self.ended_at = parse_iso_date_string(ended_at)

    def discretized_gaze_matrix(self, system_config):
        PIXELS_PER_DISCRETIZATION_UNIT = 15
        MILLISECONDS_PER_TIME_WINDOW_DISCRETIZATION = 50

        #
        duration_in_ms = math.ceil(distance_in_ms(self.ended_at, self.started_at))
        buckets_amount = math.ceil(
            duration_in_ms / MILLISECONDS_PER_TIME_WINDOW_DISCRETIZATION
        )
        def ts_to_bucket_idx(ts):
            # https://stackoverflow.com/questions/46803405/python-timedelta-object-with-negative-values
            if (ts - self.started_at).days < 0:
                raise Exception("Invalid ts")

            return math.floor(distance_in_ms)

        #
        estimated_gazes = [[] for _ in range(buckets_amount)]
        for estimation in self.estimations:
            # TODO: guardar en el arreglo todas las coordenadas que caigan
            bucket_idx = ts_to_bucket_idx(estimation)

        # TODO:
        #   - Tomar la media de las estimaciones de cada gaze
        #   - Armar la matriz y sumar en cada posición
        dgm = np.zeros((
            system_config['viewport_height'] // PIXELS_PER_DISCRETIZATION_UNIT,
            system_config['viewport_width'] // PIXELS_PER_DISCRETIZATION_UNIT,
        ))
        # TODO: Normalize the matrix so that the sum of all its values sums 100
        raise NotImplementedError('foo')
        return dgm

def reduce_js_psych_output(acc, cur):
    if cur['trial_type'] == "check-requirements":
        acc['system_config'] = {
            'viewport_width': cur['systemConfig']['viewportWidth'],
            'viewport_height': cur['systemConfig']['viewportHeight']
        }
    if cur['trial_type'] == "antisaccades":
        acc['antisaccades_outputs'].append(AntisaccadesTaskOutput(
            cur['estimationWindowData']['values'],
            cur['taskData']['startedAt'],
            cur['taskData']['endedAt'],
            'decalibration_detected' in cur and cur['decalibration_detected']
        ))
    return acc

parsed_output = reduce(
    reduce_js_psych_output,
    js_psych_output,
    { 'antisaccades_outputs': [] }
)

print([
    # TODO: For each matrix create and export a heatmap. Interpolation will be
    #       needed for the plot to make sense
    x.discretized_gaze_matrix(parsed_output['system_config'])
    for x
    in parsed_output['antisaccades_outputs']
])
