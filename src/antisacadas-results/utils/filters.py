import matplotlib.pyplot as plt

from constants import REQUIRED_FOCUS_TIME_PRE_VISUAL_CUE
from trials_collection import TrialsCollection

def drop_unfocused_trials(trials):
    focused_trials, unfocused_trials = [], []
    for t in trials.all():
        xs_before_visual_cue = [
            e['x'] for e in t['estimates']
            if - REQUIRED_FOCUS_TIME_PRE_VISUAL_CUE < e['t'] < 0
        ]
        avg = sum(xs_before_visual_cue) / len(xs_before_visual_cue)
        if any([
            x - avg > 0.3 or abs(x) > 0.5
            for x in xs_before_visual_cue
        ]):
            unfocused_trials.append(t)
        else:
            focused_trials.append(t)

    focused_trials = TrialsCollection(focused_trials)
    unfocused_trials = TrialsCollection(unfocused_trials)

    fig, axs = plt.subplots(ncols=2, nrows=2)
    for j, saccade_type in enumerate(['pro', 'anti']):
        for t in focused_trials.get_trials_by_saccade(saccade_type):
            es = t['estimates']
            axs[0][j].plot(
                [e['t'] for e in es],
                [e['x'] for e in es],
                color="black",
                alpha=0.3
            )
        for t in unfocused_trials.get_trials_by_saccade(saccade_type):
            es = t['estimates']
            axs[1][j].plot(
                [e['t'] for e in es],
                [e['x'] for e in es],
                color="red",
                alpha=0.3
            )
    plt.show()

    return focused_trials
