import sys, os, shutil

from parsing import read_subject_run
from time_utils import distance_in_ms 

from interpolation import \
        uniformly_sample_trial_gazes, \
        uniformly_sample_experiment_gazes_and_follow_up_stimulus

from plotting import plot_gaze_heatmap, plot_seguimiento

if len(sys.argv) == 1:
    raise Exception(
        "Debe pasarse el primer path del output de JSPsych como primer parámetro."
    )
[system_config, experiments, events] = read_subject_run(sys.argv[1])

if os.path.isdir('output'):
    shutil.rmtree('output')
os.mkdir('output')

for n in experiments:
    e = experiments[n]

    for trial_number, t in enumerate(e):
        trial_estimated_gazes = \
            uniformly_sample_trial_gazes(events, t)
        plot_gaze_heatmap(system_config, n, trial_number, t, trial_estimated_gazes)

    if n == 'seguimiento':
        samples = \
            uniformly_sample_experiment_gazes_and_follow_up_stimulus(events, e)
        plot_seguimiento(events, samples, e)
