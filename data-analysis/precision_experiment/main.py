import os, csv, json
from statistics import mean, stdev

class Coord():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class RawEstimation:
    def __init__(self, t, p):
        self.t = t
        self.p = p

class Run():
    def __init__(self, run_id, computer_id, webcam_id, web_browser):
        self.id = run_id
        if computer_id is None:
            raise Exception("computer id not provided")
        self.computer_id = computer_id
        if webcam_id is None:
            raise Exception("webcam id not provided")
        self.webcam_id = webcam_id
        if web_browser is None:
            raise Exception("web browser not provided")
        self.web_browser = web_browser

class Session():
    def __init__(self, run_id, session_id):
        self.run_id = run_id
        self.id = session_id

class Validation():
    def __init__(
            self,
            run_id, session_id, validation_id,
            validation_position,
            fixation_marker,
            validation_markers,
            pxs2deg):
        self.run_id = run_id
        self.session_id = session_id
        self.id = validation_id

        # number indicating the position of the validation with respect
        # to the other validations of the same session
        self.validation_position = validation_position

        self.fixation_phase_mean_pxs_to_center = \
            fixation_marker.tracked_marker.mean_pxs_to_center()
        self.fixation_phase_mean_degrees_to_center = \
            fixation_marker.tracked_marker.mean_degrees_to_center(pxs2deg)

class TrackedMarker():
    def __init__(self, r_id, s_id, v_id, tm_id, center, raw_es):
        self.run_id = r_id
        self.session_id = s_id
        self.validation_id = v_id
        self.id = tm_id
        self.center = center
        self.raw_estimations = raw_es

    def mean_pxs_to_center(self):
        MINIMUM_EXPECTED_MS_FOR_SACCADE = 250
        mean_x = mean([
            r_e.p.x
            for r_e
            in self.raw_estimations
            if r_e.t > MINIMUM_EXPECTED_MS_FOR_SACCADE])
        mean_y = mean([
            r_e.p.y
            for r_e
            in self.raw_estimations
            if r_e.t > MINIMUM_EXPECTED_MS_FOR_SACCADE])

        return Coord(
            abs(self.center.x - mean_x),
            abs(self.center.y - mean_y))

    def mean_degrees_to_center(self, pxs2deg):
        c = self.mean_pxs_to_center()
        return Coord(c.x / pxs2deg, c.y / pxs2deg)

class FixationMarker():
    def __init__(self, tracked_marker):
        self.tracked_marker = tracked_marker

class load_data():
    def __init__(self):
        if not os.path.isdir('data-analysis/precision_experiment/raw_data'):
            raise Exception('missing raw data directory')

        files_paths = os.listdir('data-analysis/precision_experiment/raw_data')
        if len(files_paths) == 0:
            raise Exception('no runs were found')

        self.runs = []
        self.sessions = []
        self.validations = []
        self.tracked_markers = []
        ids = {
            "run": 1,
            "session": 1,
            "validation": 1,
            "tracked-marker": 1,
        }
        collected_data = {
            "fixation-marker": None,
            "validation-markers": [],
            "validation-position": 0,
            "pxs2deg": None,
        }
        for fp in files_paths:
            run_sessions = []
            computer_id = None
            webcam_id = None
            web_browser = None
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
                    collected_data["validation-position"] = 0

                def finish_reading_validation():
                    if not session_reading_in_progress:
                        raise Exception('no session reading in progress')

                    self.validations.append(Validation(
                        ids["run"], ids["session"], ids["validation"],
                        collected_data["validation-position"],
                        collected_data["fixation-marker"],
                        collected_data["validation-markers"],
                        collected_data["pxs2deg"]))

                    collected_data["fixation-marker"] = None
                    collected_data["validation-markers"] = []
                    collected_data["validation-position"] += 1
                    ids["validation"] += 1

                def finish_reading_fixation_marker(tm):
                    collected_data["fixation-marker"] = FixationMarker(tm)

                def finish_reading_validation_marker(tm):
                    collected_data["validation-markers"].append(tm)

                str2float = lambda s: float(s.replace(",", "."))

                tracked_marker = None
                for row in csv_rows_iterator:
                    trial_index = row[headers.index('trial_index')]
                    rastoc_type = row[headers.index('rastoc-type')]

                    if row[headers.index('trial_type')] == 'virtual-chinrest':
                        print(row[headers.index('px2deg')])
                        collected_data["pxs2deg"] = str2float(row[headers.index('px2deg')])
                        continue

                    if row[headers.index('trial_type')] == 'survey-html-form':
                        d = json.loads(row[headers.index('response')])
                        computer_id = int(d['computer-id'])
                        webcam_id = int(d['webcam-id'])
                        web_browser = d['web-browser']
                        continue

                    is_tracked_marker = \
                        row[headers.index('rastoc-type')] == "tracked-stimulus"
                    if is_tracked_marker:
                        tracked_marker = TrackedMarker(
                            ids["run"], ids["session"],
                            ids["validation"], ids["tracked-marker"],
                            Coord(
                                str2float(row[headers.index("center_x")]),
                                str2float(row[headers.index("center_y")]),
                            ),
                            [
                                RawEstimation(e["t"], Coord(e["x"], e["y"]))
                                for e in
                                json.loads(row[headers.index('webgazer_data')])
                            ])
                        self.tracked_markers.append(tracked_marker)
                        ids["tracked-marker"] += 1

                    is_fixation_marker = \
                        row[headers.index('trial-tag')] == "fixation-stimulus"
                    is_validation_marker = \
                        row[headers.index('trial-tag')] == "validation-stimulus"

                    raw_session_id = row[headers.index("session-id")]
                    if not session_reading_in_progress and raw_session_id != '':
                        session_reading_in_progress = True

                        assert(is_fixation_marker)
                        finish_reading_fixation_marker(tracked_marker)
                    elif session_reading_in_progress and is_fixation_marker:
                        finish_reading_validation()
                        finish_reading_fixation_marker(tracked_marker)
                    elif session_reading_in_progress and is_validation_marker:
                        finish_reading_validation_marker(tracked_marker)
                    elif session_reading_in_progress and raw_session_id == '':
                        finish_reading_validation()
                        finish_reading_session()

                        session_reading_in_progress = False

            self.runs.append(Run(
                ids["run"],
                computer_id,
                webcam_id,
                web_browser
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
                print("     [ id: {}, session_id: {}, run_id: {}, validation_position: {} ]".format(
                v.id, v.session_id, v.run_id, v.validation_position
            )) for v in self.validations[:7]]
        print(" - {} tracked markers".format(len(self.tracked_markers)))
        [
                print("     [ id: {}, validation_id: {}, session_id: {}, run_id: {} ]".format(
                v.id, v.session_id, v.run_id, v.validation_id
            )) for v in self.tracked_markers[:3]]
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

    def ith_validations(self, i):
        return [v for v in self.D.validations if v.validation_position == i]

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
    print("validation-position\tfixation-phase-pxs-to-center\t\tfixation-phase-degrees-to-center\t")
    print("\tx\ty\tx\ty")
    for i in range(max_validations):
        ith_vs = q.ith_validations(i)
        pxs_to_centers = [
            v.fixation_phase_mean_pxs_to_center
            for v in ith_vs
        ]
        degrees_to_centers = [
            v.fixation_phase_mean_degrees_to_center
            for v in ith_vs
        ]
        print("{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}".format(i,
            mean([d.x for d in pxs_to_centers]),
            mean([d.y for d in pxs_to_centers]),
            mean([d.x for d in degrees_to_centers]),
            mean([d.y for d in degrees_to_centers])))
