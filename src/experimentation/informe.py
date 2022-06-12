import sys, os
import matplotlib.pyplot as plt

from instances_common.plots import separated_hist
from instances_common.plots import draw_sampling_frequecies_marks
from first_instance.summary import parse_first_instance
from second_instance.summary import parse_second_instance

def parse_instances():
    return {
        'first': parse_first_instance(),
        'second': parse_second_instance()
    }

def draw_metric(instances, metric_name, field_name):
    for j, name in enumerate(['first', 'second']):
        perRunAx = axes[0][j]
        perTrialAx = axes[1][j]
        separated_hist(
            perRunAx,
            perTrialAx,
            instances[name]['post_filtering_metrics'][metric_name],
            field_name
        )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('missing action', file=sys.stderr)
        sys.exit(-1)

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
    }}

    action = sys.argv[1]
    if action not in config.keys():
        print(
            'unkown action, valid ones are [{}]'.format(', '.join(config.keys())),
            file=sys.stderr
        )
        sys.exit(-1)

    instances = parse_instances()

    fig, axes = plt.subplots(nrows=2, ncols=2)
    fig.suptitle(config[action]['title'])
    draw_metric(
        instances,
        config[action]['metric_name'],
        config[action]['key_name']
    )
    axes[0][0].set_ylabel('Cantidad de sujetos')
    axes[1][0].set_ylabel('Cantidad de repeticiones')
    axes[1][0].set_xlabel(config[action]['unit_label'])
    axes[1][1].set_xlabel(config[action]['unit_label'])

    axes[0][0].set_title('Primera instancia, repeticiones agrupadas por sujeto')
    axes[1][0].set_title('Primera instancia, repeticiones miradas individualmente')
    axes[0][1].set_title('Segunda instancia, repeticiones agrupadas por sujeto')
    axes[1][1].set_title('Segunda instancia, repeticiones miradas individualmente')
    if action == 'frequencies':
        draw_sampling_frequecies_marks(axes[0][0])
        draw_sampling_frequecies_marks(axes[1][0])
        draw_sampling_frequecies_marks(axes[0][1])
        draw_sampling_frequecies_marks(axes[1][1])
    axes[0][1].legend()

    plt.show()

