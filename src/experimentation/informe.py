import sys, os

from first_instance.summary import parse_first_instance
from second_instance.summary import parse_second_instance

def parse_instances():
    return {
        'first': parse_first_instance(),
        'second': parse_second_instance()
    }

if __name__ == "__main__":
    instances = parse_instances()
    print('TODO: plot')
