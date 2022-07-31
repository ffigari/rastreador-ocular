from data_extraction.instances.first import load_first_instance

class Results():
    def __init__(self):
        fi = load_first_instance()
        si = SecondInstance()
        self.first_instance = fi
        self.second_instance = si

def load_results():
    return Results()
