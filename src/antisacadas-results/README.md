The `main.py` script perform the full analysis of the runs inside the `data`
directory.
The scripts below are subsections of the analysis and can be run independently:
- `fixated_trials.py`: filter for trials without fixation before target
appearance
- `saccade_detection.py`: computation of saccades
- `early_saccade_trials.py`: filter for trials with saccade during fixation phase or with early saccade
- `non_response_trials.py`: filter for trials without response
- `incorrect_trials.py`: filter for whether trials are correct or not
- `trials_response_times.py`: computation of response times
