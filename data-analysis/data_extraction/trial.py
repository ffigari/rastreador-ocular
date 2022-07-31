class Trial():
    trials_counter = 0
    def __init__(self,
            run_id,  # `run` and `subjects` are used as synonyms in the code
            trial_id,
            original_sampling_frecuency_in_hz,
            saccade_type,
            estimations,
            subject_age,
            inner_width,
            run_center_x,
            run_estimated_center_mean
        ):
        self.id = Trial.trials_counter
        Trial.trials_counter += 1
        self.run_id = run_id
        self.trial_id = trial_id
        self.original_sampling_frecuency_in_hz = original_sampling_frecuency_in_hz
        self.saccade_type = saccade_type
        self.estimations = estimations
        self.subject_age = subject_age
        self.inner_width = inner_width
        self.run_center_x = run_center_x
        self.run_estimated_center_mean = run_estimated_center_mean

