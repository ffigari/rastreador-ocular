import sys

from first_instance.summary import FirstInstanceResults
from second_instance.summary import SecondInstanceResults

# https://stackoverflow.com/a/14981125/2923526
def eprint(*args, **kwargs):
    print("[error]", *args, file=sys.stderr, **kwargs)

targets = ["trials_count", "subjects_count"]

instances = ["first", "second"]

def usage():
    j = lambda l: ", ".join(["`{}`".format(x) for x in l])
    print("""Usage:
    `python src/experimentation/raw_data_cooker.py <target> <instance>`
    where
        - `<target>` in [{}]
        - `<instance>` in [`first`, `second`]
    Whether `<instance>` is requested will depend on the requestd `<target>`""".format(
        j(targets),
        j(instances)
    ))
    sys.exit(-1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        eprint("Missing target")
        usage()

    input_target = sys.argv[1]
    if input_target not in targets:
        eprint("Incorrect target")
        usage()

    input_instance = sys.argv[2]
    if input_instance not in instances:
        eprint("Incorrect instance")
        usage()

    if len(sys.argv) < 3:
        eprint("Missing instance")
        usage()

    results = FirstInstanceResults() \
            if input_instance == "first" \
            else SecondInstanceResults()

    output = None
    if input_target == "trials_count":
        output = results.trials_count()
    elif input_target == "subjects_count":
        output = results.subjects_count()
    else:
        raise Exception(
            "This point should not be reached but `target` could not be processed"
        )

    print(output)
