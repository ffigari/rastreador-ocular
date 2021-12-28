import json

from time_utils import date_iso_string_to_datetime 

def read_subject_run(js_psych_output_file_path):
    js_psych_output_file = open(js_psych_output_file_path)
    js_psych_output = json.load(js_psych_output_file)
    js_psych_output_file.close()

    # Load data
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

    # Clean up data
    for n in experiments:
        for t in experiments[n]:
            t['startedAt'] = date_iso_string_to_datetime(t['startedAt'])
            t['endedAt'] = date_iso_string_to_datetime(t['endedAt'])
            t['relevantDataStartsAt'] = \
                date_iso_string_to_datetime(t['config']['relevantDataStartsAt']) \
                if 'relevantDataStartsAt' in t['config'] \
                else t['startedAt']
            t['relevantDataFinishesAt'] = \
                date_iso_string_to_datetime(t['config']['relevantDataFinishesAt']) \
                if 'relevantDataFinishesAt' in t['config'] \
                else t['endedAt']

            if n == 'seguimiento':
                for e in t['config']['stimulusPositions']:
                    e['ts'] = date_iso_string_to_datetime(e['ts'])
    events = sorted(events, key=lambda d: d['ts'])
    for e in events:
        e['ts'] = date_iso_string_to_datetime(e['ts'])

    return [system_config, experiments, events]

