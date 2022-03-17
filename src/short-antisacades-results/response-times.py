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

# TODO: Mirror data

# TODO: Compute response times and correcteness of trial
