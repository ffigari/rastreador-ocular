import sys
sys.path = ['/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/first_instance'] + sys.path

from utils.main import load_cleaned_up_trials
from utils.normalize import normalize
from response_times import drop_invalid_trials
from response_times import mirror_trials
from response_times import compute_correcteness_in_place
from common.constants import MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
from constants import POST_NORMALIZATION_REACTION_TRESHOLD

from common.main import Instance
from common.main import format_float
from common.main import format_percentage
from common.main import build_base_instance_tex_context
from common.main import build_attribute_template
from common.main import build_sample_template

from common.main import Sample
from common.main import WithResponseSample
from common.main import build_with_response_sample_tex_context

from common.main import Trial
from common.main import TrialsCollection

###

def build_first_instance_tex_context(fi):
    fi_name = "first"
    at = build_attribute_template(fi_name)
    st = build_sample_template(fi_name)
    return {
        at.format("antisaccades_correctness_percentage"): \
            format_percentage(fi.antisaccades_correctness_percentage()),
        **build_base_instance_tex_context(fi, fi_name),
        **build_with_response_sample_tex_context(fi.corrected_sample, st.format("corrected")),
    }

##

class FirstTrial(Trial):
    def __init__(self, parsed_trial):
        super().__init__(
            parsed_trial['run_id'],
            parsed_trial['trial_id'],
            parsed_trial['original_sampling_frecuency_in_hz'],
            "anti",
            parsed_trial['estimations'],
            int(parsed_trial['subject_data']['edad']),
            parsed_trial['inner_width'],
            parsed_trial['run_center_x'],
            parsed_trial['run_estimated_center_mean']
        )
        self.is_outlier = parsed_trial['outlier']
        self.fixation_start = parsed_trial['fixation_start']
        self.mid_start = parsed_trial['mid_start']
        self.cue_start = parsed_trial['cue_start']

class FirstInstance(Instance):
    def _load_data(self):
        return [FirstTrial(t) for t in mirror_trials(normalize(load_cleaned_up_trials()))]

    def _process_starting_sample(self, ts):
        trials_pre_processing = drop_invalid_trials([
            t for t in ts.all() if not t.is_outlier
        ])

        count_per_run = dict()
        for t in trials_pre_processing:
            if t.run_id not in count_per_run:
                count_per_run[t.run_id] = 0
            count_per_run[t.run_id] += 1
        trials_with_enough_per_run = [
            t
            for t in trials_pre_processing
            if count_per_run[t.run_id] >= MINIMUM_TRIALS_AMOUNT_PER_RUN_PER_TASK
        ]

        valid_ts, dropped_trials = [], []
        kept_runs_ids = []
        for t in ts.all():
            is_kept = len([
                te
                for te in trials_with_enough_per_run
                if te.run_id == t.run_id and te.trial_id == t.trial_id
            ])
            if is_kept:
                valid_ts.append(t)
                kept_runs_ids.append(t.run_id)
            else:
                dropped_trials.append(t)
        compute_correcteness_in_place(valid_ts)

        inlier_ts = [
            t for t in valid_ts
            if t.subject_reacted
        ]
        outlier_ts = [
            t for t in ts.all()
            if t.id not in set([t.id for t in inlier_ts])
        ]
        return TrialsCollection(outlier_ts), TrialsCollection(inlier_ts)

    def _look_for_response(self, inlier_ts):
        correct_ts = [
            t for t in inlier_ts.all()
            if t.subject_reacted and t.correct_reaction
        ]
        incorrect_ts = [
            t for t in inlier_ts.all()
            if t.subject_reacted and not t.correct_reaction
        ]
        return TrialsCollection(correct_ts), TrialsCollection(incorrect_ts)

    def _look_for_corrective_saccade(self, incorrect_ts):
        corrected_ts = []
        for t in incorrect_ts.all():
            for e in t.estimations:
                if e['t'] < t.response_time:
                    continue
                if e['x'] > - POST_NORMALIZATION_REACTION_TRESHOLD:
                    continue
                t.correction_time = e['t']
                corrected_ts.append(t)
                break
        return TrialsCollection(corrected_ts)

    def __init__(self):
        super().__init__()

        self.correct_antisaccades_sample = self.correct_sample
        self.incorrect_antisaccades_sample = self.incorrect_sample
        self.corrected_antisaccades_sample = self.corrected_sample
