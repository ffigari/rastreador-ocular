import sys, os
unwanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
wanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/second_instance'
if unwanted in sys.path:
    sys.path.remove(unwanted)
    sys.path = [wanted] + sys.path

from main import drop_runs_without_enough
from utils.parsing import parse_trials
from utils.cleaning import clean
from trials_response_times import compute_response_times_in_place
from incorrect_trials import divide_trials_by_correctness

from common.main import Instance
from common.main import build_base_instance_tex_context
from common.main import build_attribute_template

from common.main import Sample
from common.main import WithResponseSample

from common.main import Trial
from common.main import TrialsCollection

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

def build_second_instance_tex_context(si):
    si_name = "second"
    at = build_attribute_template(si_name)
    return {
        **build_base_instance_tex_context(si, si_name),
        at.format("early_subjects_count"): si.early_subjects_count(),
        at.format("antisaccades_correctness_percentage"): si.antisaccades_correctness_percentage(),
        at.format("prosaccades_correctness_percentage"): si.prosaccades_correctness_percentage(),
    }

class SecondInstance(Instance):
    def antisaccades_correctness_percentage(self):
        cas__count = self.correct_antisaccades_sample.trials_count
        total = cas__count + self.incorrect_antisaccades_sample.trials_count
        return cas__count / total

    def prosaccades_correctness_percentage(self):
        cps__count = self.correct_prosaccades_sample.trials_count
        total = cps__count + self.incorrect_prosaccades_sample.trials_count
        return cps__count / total

    def early_subjects_count(self):
        starting_ts = self.starting_sample.ts
        return len([
            run_id
            for run_id in starting_ts.runs_ids
            if starting_ts.get_trials_by_run(run_id).count() == 160
        ])

    def __init__(self):
        super().__init__()

        self.correct_antisaccades_sample = Sample(TrialsCollection([ct
            for ct in self.correct_sample.ts.all()
            if ct.saccade_type == "anti"
        ]))
        self.correct_prosaccades_sample = Sample(TrialsCollection([ct
            for ct in self.correct_sample.ts.all()
            if ct.saccade_type == "pro"
        ]))
        self.incorrect_antisaccades_sample = Sample(TrialsCollection([it
            for it in self.incorrect_sample.ts.all()
            if it.saccade_type == "anti"
        ]))
        self.incorrect_prosaccades_sample = Sample(TrialsCollection([it
            for it in self.incorrect_sample.ts.all()
            if it.saccade_type == "pro"
        ]))

    def _load_data(self):
        pts, counts_per_run = parse_trials()
        # TODO: Remove this `self.counts_per_run` variable?
        self.counts_per_run = counts_per_run
        return [SecondTrial(pt) for pt in pts]

    def _process_starting_sample(self, starting_ts):
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

    def _look_for_response(self, inlier_ts):
        # Didn't got to compute this on the second instance
        without_response_ts = TrialsCollection([])

        compute_response_times_in_place(inlier_ts)
        correct_ts, incorrect_ts = divide_trials_by_correctness(inlier_ts)

        return without_response_ts, correct_ts, incorrect_ts
