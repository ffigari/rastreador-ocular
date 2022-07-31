import sys, os
unwanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation'
wanted='/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/second_instance'
if unwanted in sys.path:
    sys.path.remove(unwanted)
    sys.path = [wanted] + sys.path

from main import drop_runs_without_enough
from utils.parsing import parse_trials
from utils.cleaning import clean
from trials_response_times import compute_response_times_in_place
from incorrect_trials import divide_trials_by_correctness
from utils.trial_utilities import second_saccade_interval


from statistics import mean, stdev

from common.main import Instance
from common.main import format_float
from common.main import format_percentage
from common.main import build_base_instance_tex_context
from common.main import build_with_response_sample_tex_context
from common.main import build_with_correction_sample_tex_context
from common.main import build_attribute_template

from common.main import Sample
from common.main import WithResponseSample
from common.main import WithCorrectionSample
from common.main import build_sample_template

from common.main import Trial
from common.main import TrialsCollection

