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
