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
from common.main import Sample
from common.main import TrialsCollection
from common.main import WithResponseSample

###

class FirstInstance(Instance):
    def load_data(self):
        return [{
            'run_id': t['run_id'],
            'is_outlier': t['outlier'],
            'estimations': t['estimations'],
            'fixation_start': t['fixation_start'],
            'mid_start': t['mid_start'],
            'cue_start': t['cue_start'],
            'trial_id': t['trial_id'],
            'id': t['id'],
            'original_sampling_frecuency_in_hz': t['original_sampling_frecuency_in_hz'],
            'subject_data': t['subject_data'],
            'inner_width': t['inner_width'],
        } for t in mirror_trials(normalize(load_cleaned_up_trials()))]

    def process_starting_sample(self, ts):
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

        inlier_ts, dropped_trials = [], []
        kept_runs_ids = []
        for t in ts.all():
            is_kept = len([
                te
                for te in trials_with_enough_per_run
                if te.run_id == t.run_id and te.trial_id == t.trial_id
            ])
            if is_kept:
                inlier_ts.append(t)
                kept_runs_ids.append(t.run_id)
            else:
                dropped_trials.append(t)

        outlier_ts = [
            t for t in ts.all()
            if t.id not in set([t.id for t in inlier_ts])
        ]

        compute_correcteness_in_place(inlier_ts)

        return \
            TrialsCollection.from_trials(outlier_ts), \
            TrialsCollection.from_trials(inlier_ts)

    def look_for_response(self, inlier_ts):
        without_response_ts = [
            t for t in inlier_ts.all()
            if not t.subject_reacted
        ]
        correct_ts = [
            t for t in inlier_ts.all()
            if t.subject_reacted and t.correct_reaction
        ]
        incorrect_ts = [
            t for t in inlier_ts.all()
            if t.subject_reacted and not t.correct_reaction
        ]
        return \
            TrialsCollection.from_trials(without_response_ts), \
            TrialsCollection.from_trials(correct_ts), \
            TrialsCollection.from_trials(incorrect_ts)

    def look_for_corrective_saccade(self, incorrect_ts):
        for t in incorrect_ts.all():
            t.subject_corrected_side = False
            for e in t.estimations:
                if e['t'] < t.reaction_time:
                    continue
                if e['x'] > - POST_NORMALIZATION_REACTION_TRESHOLD:
                    continue
                t.subject_corrected_side = True
                t.correction_reaction_time = e['t']
                break
        corrected_ts = [t for t in incorrect_ts.all() if t.subject_corrected_side]
        return TrialsCollection.from_trials(corrected_ts)

    def build_tex_context(self):
        return {
            "first__starting_sample__trials_count": self.starting_sample.trials_count,
            "first__starting_sample__subjects_count": self.starting_sample.subjects_count,
            "first__inlier_sample__trials_count": self.inlier_sample.trials_count,
            "first__inlier_sample__subjects_count": self.inlier_sample.subjects_count,
            "first__without_response_sample__trials_count": self.without_response_sample.trials_count,
            "first__correct_sample__trials_count": self.correct_sample.trials_count,
            "first__incorrect_sample__trials_count": self.incorrect_sample.trials_count,
            "first__corrected_sample__trials_count": self.corrected_sample.trials_count,
            "first__correct_sample__mean_response_time": self.correct_sample.mean_response_time,
            "first__correct_sample__stdev_response_time": self.correct_sample.stdev_response_time,
            "first__incorrect_sample__stdev_response_time": self.incorrect_sample.stdev_response_time,
            "first__incorrect_sample__mean_response_time": self.incorrect_sample.mean_response_time,
        }
