from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from statistics import mean, stdev

from constants import MINIMUM_TIME_FOR_SACCADE_IN_MS
from constants import POST_NORMALIZATION_FIXATION_TRESHOLD
from constants import POST_NORMALIZATION_REACTION_TRESHOLD
from constants import VISUAL_CUE_DURATION_IN_MS
from utils.main import load_normalized_trials
from utils.plotting import show_common_legend

def estimates_are_centered(xs):
    return max(
        abs(min(xs)), abs(max(xs))
    ) <= POST_NORMALIZATION_FIXATION_TRESHOLD

def subject_did_not_focus_fixation_marker(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t.estimations
        if t.fixation_start + MINIMUM_TIME_FOR_SACCADE_IN_MS <= e['t'] <= t.mid_start
    ])

def subject_got_distracted(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t.estimations
        if t.mid_start <= e['t'] <= t.cue_start
    ])

def subject_reacted_too_quickly(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t.estimations
        if t.cue_start <= e['t'] <= t.cue_start + MINIMUM_TIME_FOR_SACCADE_IN_MS
    ])

def divide_trials(trials):
    non_centered_trials = []
    distracted_trials = []
    too_quick_trials = []
    valid_trials = []
    for t in trials:
        if subject_did_not_focus_fixation_marker(t):
            non_centered_trials.append(t)
        elif subject_got_distracted(t):
            distracted_trials.append(t)
        elif subject_reacted_too_quickly(t):
            too_quick_trials.append(t)
        else:
            valid_trials.append(t)
    return non_centered_trials, distracted_trials, too_quick_trials, valid_trials

def drop_invalid_trials(trials):
    return divide_trials(trials)[3]

def mirror_trial(t):
    for e in t['estimations']:
        e['pre_mirroring_x'] = e['x']
        if t['cue_shown_at_left']:
            e['x'] *= -1
    return t

def mirror_trials(trials):
    return [mirror_trial(t) for t in trials]

def compute_correcteness_in_place(trials):
    for t in trials:
        t.subject_reacted = False
        for e in t.estimations:
            if e['t'] < t.cue_start + MINIMUM_TIME_FOR_SACCADE_IN_MS:
                continue
            if abs(e['x']) < POST_NORMALIZATION_REACTION_TRESHOLD:
                continue
            t.subject_reacted = True
            t.response_time = e['t']
            t.correct_reaction = e['x'] < 0
            break
