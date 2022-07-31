from statistics import mean, stdev

optional_milliseconds = lambda t: int(t) if t is not None else None
optional_mean = lambda vs: mean(vs) if len(vs) > 0 else None
optional_stdev = lambda vs: stdev(vs) if len(vs) > 1 else None
o_ms = optional_milliseconds
o_mean = optional_mean
o_stdev = optional_stdev

class Sample:
    def __init__(self, ts):
        self.ts = ts
        self.trials_count = ts.count()
        self.subjects_count = ts.subjects_count()
        trials_count_per_present_subject = [
            ts.get_trials_by_run(run_id).count()
            for run_id
            in set([t.run_id for t in ts.all()])
        ]

        self.mean_trials_count_per_subject = \
            o_mean(trials_count_per_present_subject)
        self.stdev_trials_count_per_subject = \
            o_stdev(trials_count_per_present_subject)

        self.involved_run_ids = set([ t.run_id for t in self.ts.all() ])

    def find_trial(self, run_id, trial_id):
        for t in self.ts.all():
            if t.run_id == run_id and t.trial_id == trial_id:
                return t
        raise RuntimeError(
            'trial of run_id={} and trial_id={} was not found in the sample'.format(
                run_id, trial_id))

    def subsample_by_run_id(self, run_id):
        return Sample(self.ts.get_trials_by_run(run_id))

    def per_subject_subsamples(self):
        return [
            (ri, self.subsample_by_run_id(ri))
            for ri
            in set([t.run_id for t in self.ts.all()])
        ]

class WithResponseSample(Sample):
    def __init__(self, ts):
        super().__init__(ts)
        rts = [t.response_time for t in ts.all()]
        self.mean_response_time = o_ms(o_mean(rts))
        self.stdev_response_time = o_ms(o_stdev(rts))

class WithCorrectionSample(WithResponseSample):
    def __init__(self, incorrect_ts):
        super().__init__(incorrect_ts)
        delays = [t.correction_time - t.response_time for t in incorrect_ts.all()]
        self.mean_correction_delay = o_ms(o_mean(delays))
        self.stdev_correction_delay = o_ms(o_stdev(delays))
