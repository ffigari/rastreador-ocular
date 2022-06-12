import sys, os

from first_instance.summary import parse_first_instance
from second_instance.summary import parse_second_instance

parse_first_instance()
parse_second_instance()

raise Exception('Run all')
