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
            def __init__(self, session_id, run_id):
                self.id = session_id
                self.run_id = run_id

        session_id = 1
        run_id = 1
        for fp in files_paths:
            run_sessions = []
            with open(os.path.join(
                "data-analysis/precision_experiment/raw_data", fp
            ), "r") as f:
                csv_rows_iterator = csv.reader(f, delimiter=",", quotechar='"')
                headers = next(csv_rows_iterator, None)

                for row in csv_rows_iterator:
                    trial_index = row[headers.index('trial_index')]
                    rastoc_type = row[headers.index('rastoc-type')]
                    if rastoc_type == "calibration-stimulus":
                        # inside a calibration
                        if int(row[headers.index("calibration-point-id")]) == 17:
                            # calibration finished
                            print("calibration finished")
                            # TODO: The session should be created after the 
                            # validation session, ie, once both its calibration
                            # and validation sessions have been read
                            self.sessions.append(Session(
                                session_id,
                                run_id,
                            ))
                            session_id += 1


            self.runs.append(Run(
                run_id,
                [s.run_id for s in run_sessions],
                #operating_system,
                #web_browser,
                #web_cam,
            ))
            run_id += 1
            self.sessions.extend(run_sessions)

        print("loading finished")
        print("  {} runs".format(len(self.runs)))
        [
            print(" [ id: {} ]".format(r.id))
            for r in self.runs]
        print("  {} sessions".format(len(self.sessions)))
        [
            print(" [ id: {}, run_id: {} ]".format(s.id, s.run_id))
            for s in self.sessions]


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

def analyze_precision_experiment():
    q = querier_for(load_data())

    for e in q.sessions_per_run:
        print(e["run"].id, len(e["sessions"]))

    qwe
