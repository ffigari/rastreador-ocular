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

if __name__ == "__main__":
    instances = parse_instances()

    fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle('Distribución de frecuencias de sampleo')
    for j, name in enumerate(['first', 'second']):
        perRunAx = axes[0][j]
        perTrialAx = axes[1][j]
        frequencies = instances[name]['post_filtering_metrics']['frequencies']
        separated_hist(perRunAx, perTrialAx, frequencies, 'frequency')

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

    print('TODO: Polish this plot')
    plt.show()
    print('TODO: Make figure with screen resolution per run and per trial')


