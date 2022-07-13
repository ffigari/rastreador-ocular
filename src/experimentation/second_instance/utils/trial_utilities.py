from utils.constants import EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS

def relevant_saccades(t):
    return [
        (i, j) for (i, j) in t.saccades_intervals
        if t.estimations[i]['t'] > EARLINESS_THRESHOLD_POST_VISUAL_CUE_IN_MS
    ]

def first_saccade_interval(t):
    return relevant_saccades(t)[0]

def second_saccade_interval(t):
    if len(relevant_saccades(t)) <= 1:
        return None
    return relevant_saccades(t)[1]
