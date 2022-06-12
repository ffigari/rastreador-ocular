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

def draw_metric(instances):
    for j, name in enumerate(['first', 'second']):
        perRunAx = axes[0][j]
        perTrialAx = axes[1][j]
        frequencies = instances[name]['post_filtering_metrics']['frequencies']
        separated_hist(perRunAx, perTrialAx, frequencies, 'frequency')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('missing action', file=sys.stderr)
        sys.exit(-1)

    instances = parse_instances()
    fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)
    if sys.argv[1] == 'frequencies':
        fig.suptitle('Distribución de frecuencias de sampleo')
        draw_metric(instances)

        axes[0][0].set_ylabel('Cantidad de sujetos')
        axes[1][0].set_ylabel('Cantidad de repeticiones')

        axes[1][0].set_ylabel('Frecuencia (en Hz)')
        axes[1][1].set_ylabel('Frecuencia (en Hz)')

        axes[0][0].set_title('Primera instancia, repeticiones agrupadas por sujeto')
        axes[1][0].set_title('Primera instancia, repeticiones miradas individualmente')
        axes[0][1].set_title('Segunda instancia, repeticiones agrupadas por sujeto')
        axes[1][1].set_title('Segunda instancia, repeticiones miradas individualmente')

        draw_sampling_frequecies_marks(axes[0][0])
        draw_sampling_frequecies_marks(axes[1][0])
        draw_sampling_frequecies_marks(axes[0][1])
        draw_sampling_frequecies_marks(axes[1][1])

        axes[0][1].legend()

    elif sys.argv[1] == 'resolutions':
        print('TODO: Make figure with screen resolution per run and per trial')

    plt.show()

