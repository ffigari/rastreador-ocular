import sys, os


def current_modules_names():
    return list(sys.modules.keys())

original_modules_names = current_modules_names()
def is_external_module(m):
    return any(
        m.startswith(name)
        for name
        in [
            'numpy', 'matplotlib', 'dateutil', 'PIL', '_', 'pyparsing', 'mpl',
            'Py'
        ]
    )
    
def is_own_module(m):
    return m not in original_modules_names and not is_external_module(m)

def print_ctx(tag):
    print('''
<{}'>
 - path: {}
 - cwd: {}
 - modules: {}
'''.format(
    tag,
    sys.path,
    os.getcwd(),
    [mn for mn in current_modules_names() if is_own_module(mn)]
))

from first_instance.summary import parse_first_instance
from second_instance.summary import parse_second_instance

parse_first_instance()
parse_second_instance()
raise Exception('Run all')
