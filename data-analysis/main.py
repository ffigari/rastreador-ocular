import sys

from informe.main import build_informe
from defensa.main import build_defensa
from precision_experiment.main import analyze_precision_experiment
from display import display

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "An action from [`build`, `display`] has to be chosen",
            file=sys.stderr
        )
        sys.exit(-1)

    if sys.argv[1] == "build":
        if len(sys.argv) < 3:
            print(
                "Provide one of [`informe`, `defensa`, `precision-experiment`] a second argument."
            )
            sys.exit(-1)
        
        if sys.argv[2] == 'informe':
            build_informe()
            sys.exit(0)
        elif sys.argv[2] == 'defensa':
            build_defensa()
            sys.exit(0)
        elif sys.argv[2] == 'precision-experiment':
            analyze_precision_experiment()
            sys.exit(0)


        print(
            "Invalid object to build, choose one from [`informe`, `defensa`]",
            file=sys.stderr
        )
        sys.exit(-1)
    elif sys.argv[1] == "display":
        if len(sys.argv) < 3:
            print(
                    "An object from [`subjects-trials`, `saccades-detection`, `single-trial-saccades-detection`, `sensibility-analysis`] has to be chosen"
                    )
            sys.exit(-1)
        
        if sys.argv[2] == 'subjects-trials':
            display.subject_trials()
            sys.exit(0)
        elif sys.argv[2] == 'saccades-detection':
            display.saccades_detection()
            sys.exit(0)
        elif sys.argv[2] == 'single-trial-saccades-detection':
            run_id = int(sys.argv[3])
            trial_id = int(sys.argv[4])
            display.single_trial_saccades_detection(run_id, trial_id)
            sys.exit(0)

        print(
            "Invalid object to display, choose one from [`subjects-trials`, `saccades-detection`, `single-trial-saccades-detection`]",
            file=sys.stderr
        )
        sys.exit(-1)

    print(
        "Invalid action, choose one from [`build`, `display`]",
        file=sys.stderr
    )
    sys.exit(-1)
