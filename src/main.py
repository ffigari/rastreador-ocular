import sys
import numpy as np
import json
from functools import reduce
from datetime import datetime
import math

def parse_iso_date_string(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))

def distance_in_ms(oneDatetime, anotherDatetime):
    return (oneDatetime - anotherDatetime).total_seconds() * 1000


if len(sys.argv) == 1:
    raise Exception(
        "Debe pasarse el primer path del output de JSPsych como primer parámetro."
    )

js_psych_output_file_path = sys.argv[1]
js_psych_output_file = open(js_psych_output_file_path)
js_psych_output = json.load(js_psych_output_file)
js_psych_output_file.close()

system_config = None
experiments = {}
events = []

for entry in js_psych_output:
    if 'rastocCategory' not in entry:
        continue

    if entry['rastocCategory'] == 'system':
        system_config = entry['systemConfig']
        continue

    if entry['rastocCategory'] == 'trial-instance':
        name = entry['experiment']['name']
        if name not in experiments:
            experiments[name] = []

        experiments[name].append(entry['trial'])

    events.extend(entry['events'])

events = sorted(events, key=lambda d: d['ts'])

[print(x['name']) for x in events]
[print(x) for n in experiments for x in experiments[n]]
print(system_config)

# TODO: For each trial
#         - retrieve relevant gaze estimation events
#         - perform an uniform sampling to obtain regularly interleaved data
#         - build heatmap of gaze intensity
