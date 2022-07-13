import sys, os
unwanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
wanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/second_instance'
if unwanted in sys.path:
    sys.path.remove(unwanted)
    sys.path = [wanted] + sys.path

from main import drop_runs_without_enough
from utils.parsing import parse_trials
from utils.cleaning import clean
from common.main import Instance
from common.main import Trial
from common.main import TrialsCollection
from trials_response_times import compute_response_times_in_place
from incorrect_trials import divide_trials_by_correctness

class SecondTrial(Trial):
    def __init__(self, parsed_trial):
        super().__init__(
            parsed_trial['run_id'],
            parsed_trial['trial_id'],
            parsed_trial['original_frequency'],
            parsed_trial['saccade_type'],
            parsed_trial['estimates'],
            parsed_trial['age'],
            parsed_trial['viewport_width'],
        )

class SecondInstance(Instance):
    def load_data(self):
        pts, counts_per_run = parse_trials()
        # TODO: Remove this `self.counts_per_run` variable?
        self.counts_per_run = counts_per_run
        return [SecondTrial(pt) for pt in pts]

    def process_starting_sample(self, starting_ts):
        trials_pre_processing, counts_per_run = clean(starting_ts, self.counts_per_run)
        trials_with_enough_per_run = drop_runs_without_enough(trials_pre_processing, counts_per_run)
        self.counts_per_run = counts_per_run

        kept_trials = []
        kept_runs_ids = []
        for t in starting_ts.all():
            is_kept = (t.run_id, t.trial_id) in set([
                (te.run_id, te.trial_id)
                for te in trials_with_enough_per_run.all()
            ])

            if is_kept:
                kept_trials.append(t)
                kept_runs_ids.append(t.run_id)

        inlier_ts = kept_trials
        outlier_ts = [
            t for t in starting_ts.all()
            if t.id not in set([t.id for t in inlier_ts])
        ]
        return TrialsCollection(outlier_ts), TrialsCollection(inlier_ts)

    def look_for_response(self, inlier_ts):
        # Didn't got to compute this on the second instance
        without_response_ts = TrialsCollection([])

        compute_response_times_in_place(inlier_ts)
        correct_ts, incorrect_ts = divide_trials_by_correctness(inlier_ts)

        return without_response_ts, correct_ts, incorrect_ts

    def build_tex_context(self):
        return self._build_common_tex_context("second__")

def plot_second_post_processing_trials(saccades):
    plot_post_processing_trials(saccades['anti'], 'antisacadas')
    plot_post_processing_trials(saccades['pro'], 'prosacadas')

if __name__ == "__main__":
    def after_filtering(post_filtering_metrics):
        plot_sampling_frequencies(post_filtering_metrics['frequencies'])
        plot_ages(post_filtering_metrics['ages'])
        plot_widths(post_filtering_metrics['widths'])

    plot_second_post_processing_trials(saccades)
    plot_responses_times_distributions(saccades)
