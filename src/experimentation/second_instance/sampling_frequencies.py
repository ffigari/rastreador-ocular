import matplotlib.pyplot as plt
from statistics import mean, stdev

from utils.parsing import parse_trials
from common.constants import MINIMUM_SAMPLING_FREQUENCY_IN_HZ
from common.constants import TARGET_SAMPLING_FREQUENCY_IN_HZ
from common.main import TrialsCollection

def divide_trials_by_low_frequency(trials):
    ok_trials, low_frequency_trials = [], []
    for t in trials.all():
        if t.original_sampling_frecuency_in_hz < MINIMUM_SAMPLING_FREQUENCY_IN_HZ:
            low_frequency_trials.append(t)
        else:
            ok_trials.append(t)


    return \
        TrialsCollection(ok_trials), \
        TrialsCollection(low_frequency_trials)
