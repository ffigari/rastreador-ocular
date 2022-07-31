import sys
sys.path = ['/home/francisco/eye-tracking/rastreador-ocular/src/experimentation/first_instance'] + sys.path


from common.main import format_percentage
from common.main import build_base_instance_tex_context
from common.main import build_attribute_template
from common.main import build_sample_template

from common.main import build_with_response_sample_tex_context

###

def build_first_instance_tex_context(fi):
    fi_name = "first"
    at = build_attribute_template(fi_name)
    st = build_sample_template(fi_name)
    return {
        at.format("antisaccades_correctness_percentage"): \
            format_percentage(fi.antisaccades_correctness_percentage()),
        **build_base_instance_tex_context(fi, fi_name),
        **build_with_response_sample_tex_context(fi.corrected_sample, st.format("corrected")),
    }
