import sys

from data_extraction.main import load_results

class display:
    class subject_trials:
        def __init__(_):
            r = load_results()
            raise NotImplementedError()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "An action from [`build`, `display`] has to be chosen",
            file=sys.stderr
        )
        sys.exit(-1)

    if sys.argv[1] == "build":
        raise NotImplementedError()
        sys.exit(0)
    elif sys.argv[1] == "display":
        if len(sys.argv) < 3:
            print(
                "An object from [`subjects-trials`, `saccades-detection`] has to be chosen"
            )
            sys.exit(-1)
        
        if sys.argv[2] == 'subjects-trials':
            display.subject_trials()
            sys.exit(0)
        elif sys.argv[2] == 'saccades-detection':
            raise NotImplementedError()
            sys.exit(0)

        print(
            "Invalid object to display, choose one from [`subjects-trials`, `saccades-detection`]",
            file=sys.stderr
        )
        sys.exit(-1)

    print(
        "Invalid action, choose one from [`build`, `display`]",
        file=sys.stderr
    )
    sys.exit(-1)
