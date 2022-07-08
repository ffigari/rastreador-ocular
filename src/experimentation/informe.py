import sys, os
import matplotlib.pyplot as plt

from instances_common.plots import separated_hist
from instances_common.plots import draw_sampling_frequecies_marks
from instances_common.plots import plot_post_processing_trials
from instances_common.plots import plot_responses_times_distributions
from first_instance.summary import parse_first_instance
from first_instance.summary import plot_first_post_processing_trials
from second_instance.summary import parse_second_instance
from second_instance.summary import plot_second_post_processing_trials

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

import sys
import os

sys.path = [
    '/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
] + sys.path
from first_instance.summary import FirstInstanceResults
from second_instance.summary import SecondInstanceResults

if __name__ == "__main__":
    with open('informe/resultados.tex') as input_file:
        if not os.path.exists('informe/build'):
            os.mkdir('informe/build')
        if not os.path.exists('informe/build/results'):
            os.mkdir('informe/build/results')
        with open('informe/build/results/main.tex', "w") as output_file:
            fr = FirstInstanceResults()
            sr = SecondInstanceResults()
            output_file.write(input_file.read().format(

                first__starting_sample__trials_count=\
                    fr.starting_sample.trials_count,
                first__starting_sample__subjects_count=\
                    fr.starting_sample.subjects_count,
                second__starting_sample__subjects_count=\
                    sr.starting_sample.subjects_count,

                first__inlier_sample__trials_count=\
                    fr.inlier_sample.trials_count,
                first__inlier_sample__subjects_count=\
                    fr.inlier_sample.subjects_count,

                first__without_response_sample__trials_count=\
                    fr.without_response_sample.trials_count,
                first__correct_sample__trials_count=\
                    fr.correct_sample.trials_count,
                first__incorrect_sample__trials_count=\
                    fr.incorrect_sample.trials_count,

                first__corrected_sample__trials_count=\
                    fr.corrected_sample.trials_count
            ).strip('\n'))

# TODO: Delete this content below as it gets reused for re-writing
    #with open("informe/resultados.tex") as f:
        #print(f.read().format())
#    description_targets = ['frequencies', 'resolutions', 'ages']
#    allowed_targets = \
#        description_targets + \
#        ['post_processing', 'response_times_distribution']
#    if len(sys.argv) < 2:
#        print('missing target', file=sys.stderr)
#        sys.exit(-1)
#    target = sys.argv[1]
#    if target not in allowed_targets:
#        print(
#            'unkown target, valid ones are [{}]'.format(', '.join(allowed_targets)),
#            file=sys.stderr
#        )
#        sys.exit(-1)
#
#    allowed_scopes = ['both', 'first', 'second']
#    if len(sys.argv) < 3:
#        print(
#            'missing scope, valid ones are [{}]'.format(', '.join(allowed_scopes)),
#            file=sys.stderr
#        )
#        sys.exit(-1)
#    scope = sys.argv[2]
#    if scope not in allowed_scopes:
#        print(
#            'unkown scope, valid ones are [{}]'.format(', '.join(allowed_scopes)),
#            file=sys.stderr
#        )
#        sys.exit(-1)
#
#    instances = {}
#    if scope == 'both':
#        instances['first'] = parse_first_instance()
#        instances['second'] = parse_second_instance()
#    elif scope == 'first':
#        instances['first'] = parse_first_instance()
#    else:
#        instances['second'] = parse_second_instance()
#
#    if target in description_targets:
#        plot_descriptive_histograms(instances, target, scope)
#    elif target == 'post_processing':
#        for name in instances.keys():
#            saccades = instances[name]['saccades']
#            if name == 'first':
#                plot_first_post_processing_trials(saccades)
#            elif name == 'second':
#                plot_second_post_processing_trials(saccades)
#    elif target == 'response_times_distribution':
#        for name in instances.keys():
#            saccades = instances[name]['saccades']
#            plot_responses_times_distributions(saccades)
