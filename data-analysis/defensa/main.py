import os, random
import matplotlib.pyplot as plt

from data_extraction.main import load_results
from plotting import plot

from lib.main import rm_rf

def _save_fig(figure_name, build_path, renderer):
    output_format = "png"
    output_file_name = \
        "{}.{}".format(figure_name, output_format)
    output_file_build_path = \
        "{}/{}".format(build_path, output_file_name)
    output_file_logical_path ="plots/{}".format(output_file_name)

    fig = renderer()
    rm_rf(output_file_build_path)
    plt.tight_layout()
    fig.savefig(output_file_build_path, format=output_format)
    plt.close(fig)  # https://stackoverflow.com/a/9890599/2923526

    return output_file_logical_path

class save_figure:
    class starting:
        class screens_widths:
            def __init__(_, first_sws, second_sws):
                def renderer():
                    fig = plot.starting_screens_widths(
                        first_sws, second_sws
                    ).fig
                    fig.set_size_inches(5.8, 2.5)
                    return fig

                _save_fig(
                    'screens-widths-distribution',
                    'data-analysis/defensa/plots',
                    renderer
                )

        class sampling_frequencies:
            def __init__(_, first_sfs, second_sfs):
                def renderer():
                    fig = plot.starting_sampling_frequencies(
                        first_sfs, second_sfs
                    ).fig
                    fig.set_size_inches(5.8, 2.5)
                    return fig

                _save_fig(
                    'sampling-frequencies-distribution',
                    'data-analysis/defensa/plots',
                    renderer
                )

    class output_example:
        def __init__(_, t):
            def renderer():
                fig = plot.single_trial(t).fig
                fig.set_size_inches(5.8, 2.5)
                return fig

            _save_fig(
                'output-example',
                'data-analysis/defensa/plots',
                renderer
            )

def build_defensa():
    rm_rf('data-analysis/defensa/plots')
    os.mkdir('data-analysis/defensa/plots')

    r = load_results()

    save_figure.output_example(
        r.second_instance.inlier_sample.find_trial(90, 376))
    save_figure.starting.sampling_frequencies(
        r.first_instance.post_processing_metrics.sampling_frequencies,
        r.second_instance.post_processing_metrics.sampling_frequencies
    )
    save_figure.starting.screens_widths(
        r.first_instance.post_processing_metrics.widths,
        r.second_instance.post_processing_metrics.widths
    )
