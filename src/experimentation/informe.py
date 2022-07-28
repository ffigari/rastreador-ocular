import random
import sys, os
sys.path = [
    '/home/francisco/eye-tracking/rastreador-ocular/src/experimentation',
] + sys.path

from first_instance.summary import FirstInstance
from first_instance.summary import build_first_instance_tex_context

from second_instance.summary import SecondInstance
from second_instance.summary import build_second_instance_tex_context

import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

import matplotlib.pyplot as plt
from instances_common.main import plot
from instances_common.undetected_saccades import draw_saccade_detection
from instances_common.plots import draw_pre_normalization_trials

def build_results_tex_string(results, template, build_path, logical_path):
    return template.format(
        **results.first_instance_context,
        **results.second_instance_context,
    ).strip('\n')

class Results():
    def __init__(self):
        fi = FirstInstance()
        si = SecondInstance()
        self.first_instance = fi
        self.second_instance = si
        

        self.first_instance_context = \
            build_first_instance_tex_context(fi)
        self.second_instance_context = \
            build_second_instance_tex_context(si)
    
        self.first_categorized_trials = {
            'anti': {
                'correct': fi.correct_sample.ts.all(),
                'incorrect': fi.incorrect_sample.ts.all(),
            }
        }
        self.second_categorized_trials = {
            'anti': {
                'correct': [t for t in si.correct_sample.ts.all() if t.saccade_type == 'anti'],
                'incorrect': [t for t in si.incorrect_sample.ts.all() if t.saccade_type == 'anti'],
            },
            'pro': {
                'correct': [t for t in si.correct_sample.ts.all() if t.saccade_type == 'pro'],
                'incorrect': [t for t in si.incorrect_sample.ts.all() if t.saccade_type == 'pro'],
            },
        }
###

import sys
import os
import shutil

sys.path = ['/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'] + sys.path

from shared.main import rm_rf

if __name__ == "__main__":
    r = Results()
    if len(sys.argv) > 1 and sys.argv[1] == "display-saccade-detection":
        def do(t):
            print('>> saccade detection over trial')
            print('run_id={}'.format(t.run_id))
            print('trial_id={}'.format(t.trial_id))
    
            fig, ax = plt.subplots()
            fig = draw_saccade_detection(fig, ax, t)
            plt.show()
            plt.close(fig)

        sis = r.second_instance.inlier_sample
        if len(sys.argv) > 2:
            run_id = int(sys.argv[2])
            trial_id = int(sys.argv[3])
            t = sis.find_trial(run_id, trial_id)
            do(t)
        else:
            ts = sis.ts.all()
            random.shuffle(ts)
            [do(t) for t in ts]
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "display-subjects-trials":
        #sst = r.first_instance.starting_sample.per_subject_subsamples()
        sst = r.second_instance.starting_sample.per_subject_subsamples()
        random.shuffle(sst)
        for run_id, subsample in sst:
            print('>> subject trials')
            print('run_id={}'.format(run_id))
            fig, axes = plt.subplots(nrows=3)

            ts = [t for t in subsample.ts.all() if t.saccade_type == 'anti']

            draw_pre_normalization_trials(axes[0], ts)
            axes[0].set_title('initial look')

            for t in ts:
                axes[1].plot(
                    [e['t'] for e in t.estimations],
                    [e['pre_mirroring_x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            axes[1].set_title('post normalization, pre mirroring')

            for t in ts:
                axes[2].plot(
                    [e['t'] for e in t.estimations],
                    [e['x'] for e in t.estimations],
                    color="black",
                    alpha=0.1
                )
            axes[2].set_title('final look')

            axes[1].set_ylim(-1.5, 1.5)
            axes[2].set_ylim(-1.5, 1.5)

            fig.suptitle('sujeto {}, antisacadas'.format(run_id))
            plt.show()
            plt.close(fig)

        sys.exit(0)

    rm_rf('informe/build')
    os.mkdir('informe/build')

    [
        shutil.copyfile('informe/{}'.format(fn), 'informe/build/{}'.format(fn))
        for fn in [
            'tesis.tex',
            'abstract.tex',
            'dedicatoria.tex']]

    os.mkdir('informe/build/intro')
    with open('informe/intro.tex') as i_file:
        with open('informe/build/intro/main.tex', "w") as o_file:
            o_file.write(i_file.read().format())

    os.mkdir('informe/build/metodo')
    with open('informe/metodo.tex') as i_file:
        with open('informe/build/metodo/main.tex', "w") as o_file:
            o_file.write(i_file.read())
    [
        shutil.copyfile('informe/static/{}'.format(fn), 'informe/build/metodo/{}'.format(fn))
        for fn in [
            'internal-playground.png',
            'external-playground.png']]

    os.mkdir('informe/build/results')
    with open('informe/resultados.tex') as template_file:
        with open('informe/build/results/main.tex'.format(), "w") as o_file:
            o_file.write(build_results_tex_string(
                r,
                template_file.read(),
                'informe/build/results',
                "results"
            ))

    os.mkdir('informe/build/conclu')
    with open('informe/conclu.tex') as i_file:
        with open('informe/build/conclu/main.tex', "w") as o_file:
            o_file.write(i_file.read())

    plot.disaggregated_saccades(r.first_categorized_trials, 'first', 'anti')
    plot.disaggregated_saccades(r.second_categorized_trials, 'second', 'anti')
    plot.disaggregated_saccades(r.second_categorized_trials, 'second', 'pro')
    plot.response_times_distribution(r.first_categorized_trials, 'first')
    plot.response_times_distribution(r.second_categorized_trials, 'second')

    plot.ages_distribution(
        r.first_instance.post_processing_metrics.ages, 'first')
    plot.ages_distribution(
        r.second_instance.post_processing_metrics.ages, 'second')
    plot.widths_distribution(
        r.first_instance.post_processing_metrics.widths, 'first')
    plot.widths_distribution(
        r.second_instance.post_processing_metrics.widths, 'second')
    plot.sampling_frequencies_distribution(
        r.first_instance.post_processing_metrics.sampling_frequencies, 'first')
    plot.sampling_frequencies_distribution(
        r.second_instance.post_processing_metrics.sampling_frequencies, 'second')

    plot.frecuency_by_age(
        r.first_instance.starting_sample, 'first')
    plot.frecuency_by_age(
        r.second_instance.starting_sample, 'second')

    plot.normalization_looks_example(r.second_instance.starting_sample.subsample_by_run_id(44))
    plot.skewed_estimations_examples(r.first_instance.starting_sample)
    plot.undetected_saccade_examples(r.second_instance.inlier_sample)
