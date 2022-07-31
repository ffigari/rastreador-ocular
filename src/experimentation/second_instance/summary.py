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
from common.main import format_float
from common.main import format_percentage
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

      \\begin{{tabular}}{{c|cc|cc}}
        ronda
          & \\multicolumn{{2}}{{|c}}{{antisacadas}}
          & \\multicolumn{{2}}{{|c}}{{prosacadas}} \\\\
        correctitud
          & correcto & incorrecto
          & correcto & incorrecto \\\\
        \\hline
        total
          & {act}  & {ait}  & {pct}  & {pit}  \\\\
        promedio
          & {acm}  & {aim}  & {pcm}  & {pim}  \\\\
        desvío std
          & {acsd} & {aisd} & {pcsd} & {pisd} \\\\
        \\hline
        id de sujeto & & & & \\\\
        {per_subject}
      \\end{{tabular}}
      \\caption{{Cantidad de ensayos por correctitud y por sujeto (segunda
      instancia)}}
      \\label{{tab:second-incorrect-count-per-subject}}
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
        {run_id} & {acc} & {aic} & {pcc} & {pic} \\\\""".format(
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

        at.format("early_subjects_count"): si.early_subjects_count(),
        "second__correctness_summary_table": build_correctness_table_tex_string(CorrectnesTable(si))
    }

