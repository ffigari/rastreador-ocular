import random
import sys, os
sys.path = [
    '/home/francisco/eye-tracking/rastreador-ocular/src/experimentation',
] + sys.path

from first_instance.summary import FirstInstance
from first_instance.summary import build_first_instance_tex_context

from second_instance.summary import SecondInstance
from second_instance.summary import build_second_instance_tex_context

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


    with open('informe/resultados.tex') as template_file:
        with open('informe/build/results/main.tex'.format(), "w") as o_file:
            o_file.write(build_results_tex_string(
                r,
                template_file.read(),
                'informe/build/results',
                "results"
            ))

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
