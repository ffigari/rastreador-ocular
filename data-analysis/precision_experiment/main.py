import os, csv

class load_data():
    def __init__(self):
        if not os.path.isdir('data-analysis/precision_experiment/raw_data'):
            raise Exception('missing raw data directory')

        files_paths = os.listdir('data-analysis/precision_experiment/raw_data')
        if len(files_paths) == 0:
            raise Exception('no runs were found')

        self.runs = []
        class Run():
            def __init__(
                self,
                run_id,
                #operating_system, web_browser, web_cam
            ):
                self.id = run_id
                #self.operating_system = operating_system
                #self.web_browser = web_browser
                #self.web_cam = web_cam

        self.sessions = []
        class Session():
            def __init__(self, run_id, session_id):
                self.run_id = run_id
                self.id = session_id

        self.validations = []
        class Validation():
            def __init__(self, run_id, session_id, validation_id, position):
                self.run_id = run_id
                self.session_id = session_id
                self.id = validation_id

                # number indicating the position of the validation with respect
                # to the other validations of the same session
                self.position = position

        ids = {
            "run": 1,
            "session": 1,
            "validation": 1,
        }
        for fp in files_paths:
            run_sessions = []
            with open(os.path.join(
                "data-analysis/precision_experiment/raw_data", fp
            ), "r") as f:
                csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
                headers = next(csv_rows_iterator, None)

                session_reading_in_progress = False
                def finish_reading_session():
                    self.sessions.append(Session(ids["run"], ids["session"]))
                    ids["session"] += 1
                    s = None

                def finish_reading_validation():
                    if not session_reading_in_progress:
                        raise Exception('no session reading in progress')

                    
                    # TODO: Compute position of validation in this session
                    self.validations.append(Validation(
                        ids["run"], ids["session"], ids["validation"],
                        42))
                    ids["validation"] += 1

                for row in csv_rows_iterator:
                    trial_index = row[headers.index('trial_index')]
                    rastoc_type = row[headers.index('rastoc-type')]

                    raw_session_id = row[headers.index("session-id")]
                    is_fixation_stimulus = \
                        row[headers.index('trial-tag')] == "fixation-stimulus"
                    if not session_reading_in_progress and raw_session_id != '':
                        # first validation's start of each session
                        session_reading_in_progress = True
                        print("session start", trial_index)
                        assert(is_fixation_stimulus)
                    elif session_reading_in_progress and is_fixation_stimulus:
                        finish_reading_validation()
                    elif session_reading_in_progress and raw_session_id == '':
                        print('session end', trial_index)
                        # last validation's end of each session
                        finish_reading_validation()
                        finish_reading_session()
                        session_reading_in_progress = False
                    # TODO: Identificar los momentos en los cuales termina una
                    #       validación pero que no sea la ultima


            self.runs.append(Run(
                ids["run"],
                #operating_system,
                #web_browser,
                #web_cam,
            ))
            ids["run"] += 1

        print("v------------------v")
        print("| loading finished |")
        print("+------------------+")
        print(" - {} runs".format(len(self.runs)))
        [
            print("     [ id: {} ]".format(r.id))
            for r in self.runs]
        print(" - {} sessions".format(len(self.sessions)))
        [
            print("     [ id: {}, run_id: {} ]".format(s.id, s.run_id))
            for s in self.sessions]
        print(" - {} validations".format(len(self.validations)))
        [
            print("     [ id: {}, session_id: {}, run_id: {} ]".format(
                v.id, v.session_id, v.run_id
            )) for v in self.validations]
        print("--------------------")


class querier_for():
    def __init__(self, D):
        self.D = D

    def per_run(self):
        get_by_run_id = lambda r_id: [
            s for s in self.D.sessions
            if s.run_id == r_id
        ]

        return [{
            "run": r,
            "sessions": get_by_run_id(r.id)
        } for r in self.D.runs]

    def per_session(self):
        get_by_session_id = lambda s_id: [
            v for v in self.D.validations
            if v.session_id == s_id
        ]
        return [{
            "session": s,
            "validations": get_by_session_id(s.id),
        } for s in self.D.sessions]

    def maximum_amount_of_sessions(self):
        return max([
            len(e["sessions"]) for e in self.per_run()])

    def max_amount_of_validations_in_one_session(self):
        return max([
            len(e["validations"])
            for e in self.per_session()])

    def validations_grouped_by_position(self):
        for i in range(self.maximum_amount_of_sessions()):
            yield [v for v in self.D.validations if v.position == i]


def analyze_precision_experiment():
    q = querier_for(load_data())

    print(
        "maximum amount of sessions in one run?",
        q.maximum_amount_of_sessions())

    max_validations = q.max_amount_of_validations_in_one_session()
    print(
        "maximum amount of validations in one session",
        max_validations
    )

    print("per position of validation in session:")
    print("validation-position\tfixation-phase-pxs-to-center")
    for i in range(max_validations):
        # TODO: calcular métrica
        print("{}\t{}".format(i, 42))
