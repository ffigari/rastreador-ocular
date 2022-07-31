from data_extraction.instances.first import load_first_instance
from data_extraction.instances.second import load_second_instance

class Results():
    def __init__(self):
        fi = load_first_instance()
        si = load_second_instance()
        self.first_instance = fi
        self.second_instance = si

def load_results():
    return Results()
