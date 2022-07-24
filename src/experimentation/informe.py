import sys, os
import matplotlib.pyplot as plt

from instances_common.plots import separated_hist
from instances_common.plots import draw_sampling_frequecies_marks
from instances_common.plots import plot_post_processing_trials
from instances_common.plots import plot_responses_times_distributions

def draw_compared_metric(instance, perRunAx, perTrialAx, metric_name, field_name):
    separated_hist(
        perRunAx,
        perTrialAx,
        instance['post_filtering_metrics'][metric_name],
        field_name
    )

def plot_descriptive_histograms(instances, target, scope):
    config = { 'frequencies': {
        'title': 'Distribución de frecuencias de sampleo',
        'metric_name': 'frequencies',
        'key_name': 'frequency',
        'unit_label': 'Frecuencia (en Hz)'
    }, 'resolutions': {
        'title': 'Distribución de frecuencias de anchos de pantalla',
        'metric_name': 'widths',
        'key_name': 'width',
        'unit_label': 'Ancho de pantalla (en px)'
    }, 'ages': {
        'title': 'Distribución de edades',
        'metric_name': 'ages',
        'key_name': 'age',
        'unit_label': 'Edad'
    }, 'post_processing': {}}
    nrows = 2
    ncols = 1
    if scope == 'both':
        ncols = 2

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
    fig.suptitle(config[target]['title'])
    if scope == 'both':
        for j, name in enumerate(['first', 'second']):
            draw_compared_metric(
                instances[name],
                axes[0][j],
                axes[1][j],
                config[target]['metric_name'],
                config[target]['key_name']
            )
        axes[0][0].set_ylabel('Cantidad de sujetos')
        axes[1][0].set_ylabel('Cantidad de repeticiones')
        axes[1][0].set_xlabel(config[target]['unit_label'])
        axes[1][1].set_xlabel(config[target]['unit_label'])
    
        axes[0][0].set_title('Primera instancia, repeticiones agrupadas por sujeto')
        axes[1][0].set_title('Primera instancia, repeticiones miradas individualmente')
        axes[0][1].set_title('Segunda instancia, repeticiones agrupadas por sujeto')
        axes[1][1].set_title('Segunda instancia, repeticiones miradas individualmente')
        if target == 'frequencies':
            draw_sampling_frequecies_marks(axes[0][0])
            draw_sampling_frequecies_marks(axes[1][0])
            draw_sampling_frequecies_marks(axes[0][1])
            draw_sampling_frequecies_marks(axes[1][1])
        axes[0][1].legend()
    else:
        draw_compared_metric(
            instances[scope],
            axes[0],
            axes[1],
            config[target]['metric_name'],
            config[target]['key_name']
        )
        axes[0].set_ylabel('Cantidad de sujetos')
        axes[1].set_ylabel('Cantidad de repeticiones')
        axes[1].set_xlabel(config[target]['unit_label'])

        instance_label = 'Primera' if scope == 'first' else 'Segunda'
        axes[0].set_title('{} instancia, repeticiones agrupadas por sujeto'.format(instance_label))
        axes[1].set_title('{} instancia, repeticiones miradas individualmente'.format(instance_label))
        axes[0].legend()

    plt.show()

###

import random
import sys
sys.path = [
    '/home/francisco/eye-tracking/rastreador-ocular/src/experimentation',
] + sys.path

from first_instance.summary import FirstInstance
from first_instance.summary import build_first_instance_tex_context

from second_instance.summary import SecondInstance
from second_instance.summary import build_second_instance_tex_context

from instances_common.main import plot
from instances_common.undetected_saccades import draw_saccade_detection

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
        

        # TODO: Estos contextos capaz convenga crearlos donde se los usa
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

    rm_rf('informe/build')
    os.mkdir('informe/build')

    with open('informe/tesis.tex') as i_file:
        with open('informe/build/tesis.tex', "w") as o_file:
            o_file.write(i_file.read())

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
            'external-playground.png',
            'sampling-frequency-distribution.png',
            'widths-distribution.png']]

    os.mkdir('informe/build/results')
    with open('informe/resultados.tex') as template_file:
        with open('informe/build/results/main.tex'.format(), "w") as o_file:
            o_file.write(build_results_tex_string(
                r,
                template_file.read(),
                'informe/build/results',
                "results"
            ))
    [
        shutil.copyfile('informe/static/{}'.format(fn), 'informe/build/results/{}'.format(fn))
        for fn in [
            'skewed-estimations.png']]

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
    plot.frecuency_by_age(
        r.second_instance.starting_sample, 'second')
    plot.undetected_saccade_example(r.second_instance.inlier_sample)
