class TrialsCollection:
    def __init__(self, parsed_trials):
        raise RuntimeError('TODO: Delete this class in favor of the new one')
        self.parsed_trials = parsed_trials
        self.runs_ids = list(set([
            pt['run_id']
            for pt in parsed_trials
        ]))

    @property
    def runs_count(self):
        return len(self.runs_ids)

    def get_trials_by_saccade(self, saccade_type):
        return [
            t for t in self.parsed_trials
            if t['saccade_type'] == saccade_type
        ]

    def all(self):
        return self.parsed_trials

    @property
    def count(self):
        return len(self.parsed_trials)
