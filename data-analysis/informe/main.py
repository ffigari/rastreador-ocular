import shutil, os

from data_extraction.main import load_results

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

def format_float(f):
    return str((int(f * 100) / 100))

def format_percentage(p):
    return str((int(p * 10000) / 100))

def build_attribute_template(host_name):
    return "{}__{{}}".format(host_name)

def build_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        at.format("trials_count"): sample.trials_count,
        at.format("subjects_count"): sample.subjects_count,
    }

def build_sample_template(instance_name):
    return "{}__{{}}_sample".format(instance_name)

def build_with_response_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        **build_sample_tex_context(sample, sample_name),
        at.format("stdev_response_time"): sample.stdev_response_time,
        at.format("mean_response_time"): sample.mean_response_time,
    }

def build_with_correction_sample_tex_context(sample, sample_name):
    at = build_attribute_template(sample_name)
    return {
        **build_with_response_sample_tex_context(sample, sample_name),
        at.format("stdev_correction_delay"): sample.stdev_correction_delay,
        at.format("mean_correction_delay"): sample.mean_correction_delay,
    }

def build_base_instance_tex_context(bi, instance_name):
    st = build_sample_template(instance_name)
    at = build_attribute_template(instance_name)
    return {
        **build_sample_tex_context(bi.starting_sample, st.format("starting")),
        **build_sample_tex_context(bi.inlier_sample, st.format("inlier")),
        **build_with_response_sample_tex_context(bi.correct_sample, st.format("correct")),
        **build_with_response_sample_tex_context(bi.incorrect_sample, st.format("incorrect")),
        at.format("kept_trials_percentage"): \
            format_percentage(bi.inlier_sample.trials_count / bi.starting_sample.trials_count),
        at.format("kept_subjects_percentage"): \
            format_percentage(bi.inlier_sample.subjects_count / bi.starting_sample.subjects_count),
        at.format("antisaccades_correctness_percentage"): \
            format_percentage(bi.antisaccades_correctness_percentage()),
        at.format("antisaccades_correction_percentage"): \
            format_percentage(bi.antisaccades_correction_percentage()),
        at.format("mean_incorrect_antisaccades_count_per_subject"): \
            format_float(bi.mean_incorrect_antisaccades_count_per_subject()),
        **build_with_response_sample_tex_context(
            bi.correct_antisaccades_sample,
            st.format("correct_antisaccades")),
        **build_with_response_sample_tex_context(
            bi.incorrect_antisaccades_sample,
            st.format("incorrect_antisaccades")),
        **build_with_correction_sample_tex_context(
            bi.corrected_antisaccades_sample,
            st.format("corrected_antisaccades")),
    }

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

def build_results_tex_string(results, template, build_path, logical_path):
    return template.format(
        **build_first_instance_tex_context(results.first_instance),
        **build_second_instance_tex_context(results.second_instance),
    ).strip('\n')

# https://stackoverflow.com/a/9559881/2923526
def rm_rf(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

def build_informe():
    rm_rf('data-analysis/informe/build')

    os.mkdir('data-analysis/informe/build')
    os.mkdir('data-analysis/informe/build/intro')
    os.mkdir('data-analysis/informe/build/metodo')
    os.mkdir('data-analysis/informe/build/results')
    os.mkdir('data-analysis/informe/build/conclu')

    shutil.copyfile(
        'data-analysis/informe/intro.tex',
        'data-analysis/informe/build/intro/main.tex'
    )
    shutil.copyfile(
        'data-analysis/informe/metodo.tex',
        'data-analysis/informe/build/metodo/main.tex'
    )
    r = load_results()
    with open('data-analysis/informe/resultados.tex') as template_file:
        with open('data-analysis/informe/build/results/main.tex'.format(), "w") as o_file:
            o_file.write(build_results_tex_string(
                r,
                template_file.read(),
                'data-analysis/informe/build/results',
                "results"
            ))
    shutil.copyfile(
        'data-analysis/informe/conclu.tex',
        'data-analysis/informe/build/conclu/main.tex'
    )
    [
        shutil.copyfile(
            'data-analysis/informe/{}'.format(fn),
            'data-analysis/informe/build/{}'.format(fn))
        for fn in [
            'tesis.tex',
            'abstract.tex',
            'dedicatoria.tex']]
    [
        shutil.copyfile(
            'data-analysis/informe/static/{}'.format(fn),
            'data-analysis/informe/build/metodo/{}'.format(fn))
        for fn in [
            'internal-playground.png',
            'external-playground.png']]

    print('Informe built at `data-analysis/informe/build`')
