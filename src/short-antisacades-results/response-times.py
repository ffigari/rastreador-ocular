import matplotlib.pyplot as plt

from utils.main import load_normalized_trials

trials = load_normalized_trials()
fix, ax = plt.subplots()
for t in trials:
    if t['outlier']:
        raise Exception("outliers should have been filtered out at this point")
    ax.plot(
        [e['t'] for e in t['estimations']],
        [e['x'] for e in t['estimations']],
        color="black",
        alpha=0.1
    )
plt.show()

def mirror_trial(t):
    if t['cue_shown_at_left']:
        for e in t['estimations']:
            e['x'] *= -1
    return t

trials = [mirror_trial(t) for t in trials]
fix, ax = plt.subplots()
for t in trials:
    if t['outlier']:
        raise Exception("outliers should have been filtered out at this point")
    ax.plot(
        [e['t'] for e in t['estimations']],
        [e['x'] for e in t['estimations']],
        color="black",
        alpha=0.1
    )
plt.show()

# TODO: Compute response times and correcteness of trial
#       Plot them in a grid where one axis is the response time and the other
#       one is the correcteness

