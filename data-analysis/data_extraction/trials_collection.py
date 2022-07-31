class TrialsCollection:
    def __init__(self, ts):
        self.trials = ts
        self.runs_ids = set([t.run_id for t in ts])

    def count(self):
        return len(self.trials)

    def subjects_count(self):
        return len(list(set([t.run_id for t in self.trials])))

    def all(self):
        return self.trials

    def get_trials_by_run_by_saccade(self, run_id, saccade_type):
        return [
            t for t in self.trials
            if t.run_id == run_id and t.saccade_type == saccade_type
        ]

    def get_trials_by_run(self, run_id):
        return TrialsCollection([t for t in self.trials if t.run_id == run_id])
