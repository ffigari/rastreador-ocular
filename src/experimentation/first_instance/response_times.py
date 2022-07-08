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
        in t['estimations']
        if t['fixation_start'] + MINIMUM_TIME_FOR_SACCADE_IN_MS <= e['t'] <= t['mid_start']
    ])

def subject_got_distracted(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t['estimations']
        if t['mid_start'] <= e['t'] <= t['cue_start']
    ])

def subject_reacted_too_quickly(t):
    return not estimates_are_centered([
        e['x']
        for e
        in t['estimations']
        if t['cue_start'] <= e['t'] <= t['cue_start'] + MINIMUM_TIME_FOR_SACCADE_IN_MS
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
    if t['cue_shown_at_left']:
        for e in t['estimations']:
            e['x'] *= -1
    return t

def mirror_trials(trials):
    return [mirror_trial(t) for t in trials]

def compute_correcteness_in_place(trials):
    for t in trials:
        t['subject_reacted'] = False
        for e in t['estimations']:
            if e['t'] < t['cue_start'] + MINIMUM_TIME_FOR_SACCADE_IN_MS:
                continue
            if abs(e['x']) < POST_NORMALIZATION_REACTION_TRESHOLD:
                continue
            t['subject_reacted'] = True
            t['reaction_time'] = e['t']
            t['correct_reaction'] = e['x'] < 0
            break

if __name__ == "__main__":
    trials = load_normalized_trials()
    previous_count = len(trials)
    non_centered_trials, distracted_trials, too_quick_trials, valid_trials = \
        divide_trials(trials)
    trials = valid_trials
    next_count = len(trials)

    print(
        "%d trials out of %d were discarded due to subjects getting distracted from their goal" % (
        previous_count - next_count,
        previous_count
    ))

    fig, ax = plt.subplots()
    for (label, color, ts) in [
        ("repeticiones sin fijación central", "red", non_centered_trials),
        ("repeticiones con distracción", "green", distracted_trials),
        ("repeticiones con reacción demasiado rápida", "blue", too_quick_trials),
        ("repeticiones válidas", "black", trials),
    ]:
        for i, t in enumerate(ts):
            label_kwarg = dict()
            if i == 0:
                # this is so that the lable is added only once
                label_kwarg['label'] = label
            ax.plot(
                [e['t'] for e in t['estimations']],
                [e['x'] for e in t['estimations']],
                color=color,
                alpha=0.2 if color not in ["black", "red"] else 0.05,
                **label_kwarg
            )
    ax.set_title("Descarte de repeticiones")
    show_common_legend(fig, [[ax]])
    plt.show()

    trials = mirror_trials(trials)
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
    ax.set_title("Espejado de estimaciones")
    plt.show()

    compute_correcteness_in_place(trials)

    no_reaction_trials = [
        t
        for t
        in trials
        if not t['subject_reacted']
    ]
    correct_trials = [
        t
        for t
        in trials
        if t['subject_reacted'] and t['correct_reaction']
    ]
    incorrect_trials = [
        t
        for t
        in trials
        if t['subject_reacted'] and not t['correct_reaction']
    ]

    tc = len(correct_trials)
    ti = len(incorrect_trials)
    tn = len(no_reaction_trials)
    t = tc + ti + tn
    print("""
    respuesta  || correcta | incorrecta | sin respuesta
    cantidad   || %d | %d | %d
    proporción || %f | %f | %f
    """ % (
        tc, ti, tn,
        tc / t, ti / t, tn / t
    ))
    fix, axs = plt.subplots(nrows=3, sharex=True)
    for ax in axs:
        ax.axhline(
            POST_NORMALIZATION_REACTION_TRESHOLD,
            linestyle="--"
        )
        ax.axhline(
            -POST_NORMALIZATION_REACTION_TRESHOLD,
            linestyle="--"
        )
    for t in correct_trials:
        axs[0].plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
        axs[0].set_title("repeticiones correctas")
    for t in incorrect_trials:
        axs[1].plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
        axs[1].set_title("repeticiones incorrectas")
    for t in no_reaction_trials:
        axs[2].plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
        axs[2].set_title("repeticiones sin respuesta")
    plt.show()

    # TODO: This scope should not be needed anymore
    # for t in incorrect_trials:
    #     t['subject_corrected_side'] = False
    #     for e in t['estimations']:
    #         if e['t'] < t['reaction_time']:
    #             continue
    #         if e['x'] > - POST_NORMALIZATION_REACTION_TRESHOLD:
    #             continue
    #         t['subject_corrected_side'] = True
    #         t['correction_reaction_time'] = e['t']
    #         break
    # incorrect_corrected_trials = [t for t in incorrect_trials if t['subject_corrected_side']]
    # incorrect_non_corrected_trials = [t for t in incorrect_trials if not t['subject_corrected_side']]
    # tic = len(incorrect_trials)
    # tinc = len(incorrect_non_corrected_trials)
    # t = tic + tinc

    print("""
    repetición corregida || sí | no
    cantidad             || %d | %d
    proporción           || %f | %f
    """ % (tic, tinc, tic / t, tinc / t))
    fig, axs = plt.subplots(nrows=2, sharex=True)
    for t in incorrect_trials:
        ax = axs[0 if t['subject_corrected_side'] else 1]
        ax.plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
    axs[0].set_title("repeticiones incorrectas con corrección")
    axs[1].set_title("repeticiones incorrectas sin corrección")
    fig.suptitle("Correcciones")
    plt.show()

    BUCKETS_AMOUNT = 5
    trials = correct_trials
    trials.extend(incorrect_trials)
    fig, axs = plt.subplots(nrows=BUCKETS_AMOUNT, ncols=2, sharex=True, sharey=True)
    buckets_trials_count = [[0] * 2 for _ in range (BUCKETS_AMOUNT)]
    for t in trials:
        b = min(
            BUCKETS_AMOUNT - 1,
            int(t['reaction_time'] // (VISUAL_CUE_DURATION_IN_MS // BUCKETS_AMOUNT))
        )
        j = 0 if t['correct_reaction'] else 1
        axs[b][j].plot(
            [e['t'] for e in t['estimations']],
            [e['x'] for e in t['estimations']],
            color="black",
            alpha=0.1
        )
        buckets_trials_count[b][j] += 1

    size = VISUAL_CUE_DURATION_IN_MS / BUCKETS_AMOUNT
    for b in range(BUCKETS_AMOUNT):
        for i in range(2):
            if buckets_trials_count[b][i] == 0:
                continue
            axs[b][i].add_patch(Rectangle(
                (b * size, 1), size, -2,
                color='red', alpha=0.1
            ))
    axs[0][0].set_title("respuesta correcta")
    axs[0][1].set_title("respuesta incorrecta")
    fig.suptitle("""Repeticiones desagregregadas
    según tipo y tiempo de respuesta""")
    plt.show()

    # correct_response_times = [t['reaction_time'] for t in correct_trials]
    # incorrect_response_times = [t['reaction_time'] for t in incorrect_trials]
    print("""tiempo de respuesta
    tipo  | correcto | incorrecto
    mean  | %f | %f
    stdev | %f | %f""" % (
        mean(correct_response_times), mean(incorrect_response_times),
        stdev(correct_response_times), stdev(incorrect_response_times)
    ))
