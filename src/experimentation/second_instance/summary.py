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
from utils.trial_utilities import second_saccade_interval


from statistics import mean, stdev

from common.main import Instance
from common.main import build_base_instance_tex_context
from common.main import build_with_response_sample_tex_context
from common.main import build_with_correction_sample_tex_context
from common.main import build_attribute_template

from common.main import Sample
from common.main import WithResponseSample
from common.main import WithCorrectionSample
from common.main import build_sample_template

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

def format_float(f):
    return str((int(f * 100) / 100))

def format_percentage(p):
    return str((int(p * 10000) / 100))

def union(*ss):
    return set().union(*ss)

def build_correctness_table_tex_string(ct):
    acs = ct.correct_antisaccades_sample
    ais = ct.incorrect_antisaccades_sample
    pcs = ct.correct_prosaccades_sample
    pis = ct.incorrect_prosaccades_sample
    involved_run_ids = union(
        acs.involved_run_ids,
        ais.involved_run_ids,
        pcs.involved_run_ids,
        pis.involved_run_ids,
    )
    return """
    \\begin{{table}}[htb]
        \\centering
        \\caption{{Cantidad de ensayos por resultado y por sujeto (segunda
        instancia)}}

        % TODO: Armar tabla tex

              || anti            || pro             \\\\
              || corr   | incorr || corr   | incorr \\\\
        total || {act}  | {ait}  || {pct}  | {pit}  \\\\
        mean  || {acm}  | {aim}  || {pcm}  | {pim}  \\\\
        stdev || {acsd} | {aisd} || {pcsd} | {pisd} \\\\
        ------------------------------------------- \\\\
        {per_subject}

        Los sujetos involucrados en esta tabla son aquellos que obtuvieron
        suficiente cantidad de ensayos luegos de aplicar los criterios de 
        filtrado.
        Todo sujeto termina con una cantidad no significativa de ensayos en
        ambos grupos incorrectos, algunos realizando incluso correctamente todo
        sus ensayos.
        \\label{{tab:correctness}}
    \\end{{table}}
    """.format(
        act=acs.trials_count,
        acm=format_float(acs.mean_trials_count_per_subject),
        acsd=format_float(acs.stdev_trials_count_per_subject),

        ait=ais.trials_count,
        aim=format_float(ais.mean_trials_count_per_subject),
        aisd=format_float(ais.stdev_trials_count_per_subject),

        pct=pcs.trials_count,
        pcm=format_float(pcs.mean_trials_count_per_subject),
        pcsd=format_float(pcs.stdev_trials_count_per_subject),

        pit=pis.trials_count,
        pim=format_float(pis.mean_trials_count_per_subject),
        pisd=format_float(pis.stdev_trials_count_per_subject),

        per_subject="".join(["""
        {run_id} || {acc} | {aic} || {pcc} | {pic} \\\\""".format(
            run_id=run_id,
            **counts,
        ) for run_id, counts in dict([(run_id, {
            "acc": ac_ss.trials_count,
            "aic": ai_ss.trials_count,
            "pcc": pc_ss.trials_count,
            "pic": pi_ss.trials_count,
        }) for run_id, (ac_ss, ai_ss, pc_ss, pi_ss) in dict([(run_id, [
            acs.subsample_by_run_id(run_id),
            ais.subsample_by_run_id(run_id),
            pcs.subsample_by_run_id(run_id),
            pis.subsample_by_run_id(run_id),
        ]) for run_id in involved_run_ids]).items()]).items()]),
    )

class CorrectnesTable():
    def __init__(self, second_instance):
        self.incorrect_antisaccades_sample = \
            second_instance.incorrect_antisaccades_sample
        self.correct_antisaccades_sample = \
            second_instance.correct_antisaccades_sample
        self.incorrect_prosaccades_sample = \
            second_instance.incorrect_prosaccades_sample
        self.correct_prosaccades_sample = \
            second_instance.correct_prosaccades_sample

def build_second_instance_tex_context(si):
    si_name = "second"
    instance_name = si_name
    at = build_attribute_template(instance_name)
    st = build_sample_template(instance_name)
    return {
        **build_base_instance_tex_context(si, instance_name),

        at.format("prosaccades_correctness_percentage"): \
            format_percentage(si.prosaccades_correctness_percentage()),
        at.format("mean_incorrect_prosaccades_count_per_subject"): \
            format_float(si.mean_incorrect_prosaccades_count_per_subject()),
        **build_with_response_sample_tex_context(
            si.correct_prosaccades_sample,
            st.format("correct_prosaccades")),
        **build_with_response_sample_tex_context(
            si.incorrect_prosaccades_sample,
            st.format("incorrect_prosaccades")),

        at.format("antisaccades_correctness_percentage"): \
            format_percentage(si.antisaccades_correctness_percentage()),
        at.format("antisaccades_correction_percentage"): \
            format_percentage(si.antisaccades_correction_percentage()),
        at.format("mean_incorrect_antisaccades_count_per_subject"): \
            format_float(si.mean_incorrect_antisaccades_count_per_subject()),
        **build_with_response_sample_tex_context(
            si.correct_antisaccades_sample,
            st.format("correct_antisaccades")),
        **build_with_response_sample_tex_context(
            si.incorrect_antisaccades_sample,
            st.format("incorrect_antisaccades")),
        **build_with_correction_sample_tex_context(
            si.corrected_antisaccades_sample,
            st.format("corrected_antisaccades")),

        at.format("early_subjects_count"): si.early_subjects_count(),
        "second__correctness_summary_table": build_correctness_table_tex_string(CorrectnesTable(si))
    }

class SecondInstance(Instance):
    def mean_incorrect_prosaccades_count_per_subject(self):
        return self.incorrect_prosaccades_sample.mean_trials_count_per_subject

    def mean_incorrect_antisaccades_count_per_subject(self):
        return self.incorrect_antisaccades_sample.mean_trials_count_per_subject

    def antisaccades_correction_percentage(self):
        return \
                self.corrected_antisaccades_sample.trials_count / \
                self.incorrect_antisaccades_sample.trials_count 

    def antisaccades_correctness_percentage(self):
        cas__count = self.correct_antisaccades_sample.trials_count
        return cas__count / (cas__count + self.incorrect_antisaccades_sample.trials_count)

    def prosaccades_correctness_percentage(self):
        cps__count = self.correct_prosaccades_sample.trials_count
        return cps__count / (cps__count + self.incorrect_prosaccades_sample.trials_count)

    def early_subjects_count(self):
        starting_ts = self.starting_sample.ts
        return len([
            run_id
            for run_id in starting_ts.runs_ids
            if starting_ts.get_trials_by_run(run_id).count() == 160
        ])

    def __init__(self):
        super().__init__()

        self.correct_prosaccades_sample = WithResponseSample(TrialsCollection([
            ct
            for ct in self.correct_sample.ts.all()
            if ct.saccade_type == "pro"
        ]))
        self.incorrect_prosaccades_sample = WithResponseSample(TrialsCollection([
            it
            for it in self.incorrect_sample.ts.all()
            if it.saccade_type == "pro"
        ]))

        self.correct_antisaccades_sample = WithResponseSample(TrialsCollection([
            ct
            for ct in self.correct_sample.ts.all()
            if ct.saccade_type == "anti"
        ]))
        self.incorrect_antisaccades_sample = WithResponseSample(TrialsCollection([
            it
            for it in self.incorrect_sample.ts.all()
            if it.saccade_type == "anti"
        ]))
        self.corrected_antisaccades_sample = WithCorrectionSample(TrialsCollection([
            ct
            for ct in self.corrected_sample.ts.all()
            if ct.id in set([
                iat.id
                for iat in self.incorrect_antisaccades_sample.ts.all()
            ])
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

    def _look_for_corrective_saccade(self, incorrect_ts):
        corrected_ts = []
        for t in incorrect_ts.all():
            second_saccade_indexes = second_saccade_interval(t)
            second_saccade_was_detected = second_saccade_indexes is not None
            if second_saccade_was_detected:
                t.correction_time = t.estimations[second_saccade_indexes[0]]['t']
                corrected_ts.append(t)
            
        return TrialsCollection(corrected_ts)
