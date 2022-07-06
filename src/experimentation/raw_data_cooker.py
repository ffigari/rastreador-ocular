import sys

from first_instance.summary import FirstInstanceResults
from second_instance.summary import SecondInstanceResults

# https://stackoverflow.com/a/14981125/2923526
def eprint(*args, **kwargs):
    print("[error]", *args, file=sys.stderr, **kwargs)

instances = ["first", "second"]

def usage():
    print("""Usage:
    `python src/experimentation/raw_data_cooker.py <target> <instance>`
    where
        - `<target>`
        - `<instance>` in [`first`, `second`]
    Whether `<instance>` is requested will depend on the requestd `<target>`"""
    )
    sys.exit(-1)


def cook_target_results(input_target, input_instance):
    r = FirstInstanceResults() \
        if input_instance == "first" \
        else SecondInstanceResults()
    [(r := getattr(r, t)) for t in input_target.split(".")]
    return r

if __name__ == "__main__":
    if len(sys.argv) < 2:
        eprint("Missing target")
        usage()
    input_target = sys.argv[1]

    if len(sys.argv) < 3:
        eprint("Missing instance")
        usage()
    input_instance = sys.argv[2]
    if input_instance not in instances:
        eprint("Incorrect instance")
        usage()

    r = str(cook_target_results(input_target, input_instance))
    if input_target == "inliering_sample_count_stats.trials_count" and input_instance == "first":
        assert("713" == r)
        print("[info] passing", file=sys.stderr)
    print(r)
