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
                run_id, sessions_ids,
                #operating_system, web_browser, web_cam
            ):
                self.id = run_id
                self.sessions_ids = sessions_ids
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

        run_id = 1
        session_id = 1
        for fp in files_paths:
            run_sessions = []
            with open(os.path.join(
                "data-analysis/precision_experiment/raw_data", fp
            ), "r") as f:
                csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
                headers = next(csv_rows_iterator, None)

                run_inner_session_id = None
                for row in csv_rows_iterator:
                    trial_index = row[headers.index('trial_index')]
                    rastoc_type = row[headers.index('rastoc-type')]
                    raw_session_id = row[headers.index("session-id")]
                    print(run_id, trial_index, raw_session_id)
                    if run_inner_session_id is None and raw_session_id != '':
                        run_inner_session_id = int(raw_session_id)
                    elif run_inner_session_id is not None and raw_session_id == '':
                        run_sessions.append(Session(
                            run_id,
                            session_id,
                        ))
                        session_id += 1
                        run_inner_session_id = None

            self.runs.append(Run(
                run_id,
                [s.run_id for s in run_sessions],
                #operating_system,
                #web_browser,
                #web_cam,
            ))
            run_id += 1
            self.sessions.extend(run_sessions)

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
        print("--------------------")


class querier_for():
    def __init__(self, D):
        self.D = D

    @property
    def sessions_per_run(self):
        get_by_run_id = lambda r_id: [
            s for s in self.D.sessions
            if s.run_id == r_id
        ]

        return [{
            "run": r,
            "sessions": get_by_run_id(r.id)
        } for r in self.D.runs]

    def maximum_amount_of_sessions(self):
        return max([
            len(e["sessions"]) for e in self.sessions_per_run])

    def validations_grouped_by_position(self):
        for i in range(self.maximum_amount_of_sessions()):
            yield [v for v in self.D.validations if v.position == i]


def analyze_precision_experiment():
    q = querier_for(load_data())

    print(
        "maximum amount of sessions in one run?",
        q.maximum_amount_of_sessions())

    #print("average estimation during fixation marks")
    #print("run_position\taverage_fixation_error")
    #[handle_list_of_the_ith_validations(ith_vs)
    #    for ith_vs in q.validations_grouped_by_position()]
