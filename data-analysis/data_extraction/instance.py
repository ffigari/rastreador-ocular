from data_extraction.trials_collection import TrialsCollection
from data_extraction.sample import Sample
from data_extraction.sample import WithResponseSample
from data_extraction.sample import WithCorrectionSample

class PostProcessingMetrics:
    def __init__(self, inlier_sample, outlier_sample):
        self.sampling_frequencies, self.ages, self.widths = [], [], []
        for kept, ts in [(True, inlier_sample.ts), (False, outlier_sample.ts)]:
            for t in ts.all():
                self.sampling_frequencies.append({
                    'frequency': t.original_sampling_frecuency_in_hz,
                    'run_id': t.run_id,
                    'kept': kept,
                })
                self.ages.append({
                    'age': t.subject_age,
                    'run_id': t.run_id,
                    'kept': kept,
                })
                self.widths.append({
                    'width': t.inner_width,
                    'run_id': t.run_id,
                    'kept': kept,
                })

class Instance():
    def mean_incorrect_antisaccades_count_per_subject(self):
        return self.incorrect_antisaccades_sample.mean_trials_count_per_subject

    def antisaccades_correction_percentage(self):
        return \
                self.corrected_antisaccades_sample.trials_count / \
                self.incorrect_antisaccades_sample.trials_count 

    def antisaccades_correctness_percentage(self):
        cas__count = self.correct_antisaccades_sample.trials_count
        return cas__count / (cas__count + self.incorrect_antisaccades_sample.trials_count)

    def _load_data(self):
        raise NotImplementedError('Instance._load_data')

    def _process_starting_sample(self, starting_ts):
        raise NotImplementedError('Instance._process_starting_sample')

    def _look_for_response(self, inlier_ts):
        raise NotImplementedError('Instance._look_for_response')

    def _look_for_corrective_saccade(self, incorrect_ts):
        raise NotImplementedError('Instance._look_for_corrective_saccade')

    def __init__(self):
        starting_ts = TrialsCollection(self._load_data())
        self.starting_sample = Sample(starting_ts)
        outlier_ts, inlier_ts = self._process_starting_sample(starting_ts)
        self.inlier_sample = Sample(inlier_ts)
        self.post_processing_metrics = \
            PostProcessingMetrics(self.inlier_sample, Sample(outlier_ts))

        correct_ts, incorrect_ts = self._look_for_response(inlier_ts)
        self.correct_sample = WithResponseSample(correct_ts)
        self.incorrect_sample = WithResponseSample(incorrect_ts)

        corrected_ts = self._look_for_corrective_saccade(self.incorrect_sample.ts)
        self.corrected_sample = WithCorrectionSample(corrected_ts)
