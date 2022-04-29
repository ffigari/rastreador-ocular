from utils.interpolate import interpolate_with

class Normalizer:
    def __init__(self, stimulus_results, validation_was_successful):
        print('producing new normalizer', validation_was_successful)
        [print(s) for s in stimulus_results]

        regions_of_interest = ['center', 'left', 'right']
        validated_positions_average_x_estimate = dict()
        validated_positions_real_x = dict()
        for p in regions_of_interest:
            validated_positions_average_x_estimate[p] = 0
        for p in regions_of_interest:
            for r in [r for r in stimulus_results if r['position'] == p]:
                validated_positions_real_x[p] = r['real-stimulus-x']
                es = [e['x'] for e in r['last-estimates']]
                validated_positions_average_x_estimate[p] += sum(es) / len(es)
        for p in regions_of_interest:
            validated_positions_average_x_estimate[p] /= 2

        # TODO: Real coordinates (eg, the ones from stimulus) and estimated
        #       coordinates should be normalized distinctly using the two
        #       variables below
        print(validated_positions_average_x_estimate)
        print(validated_positions_real_x)
        self.center_mapping = (
            validated_positions_average_x_estimate['center'],
            0
        )
        self.left_mapping = (
            validated_positions_average_x_estimate['left'],
            -1
        )
        self.right_mapping = (
            validated_positions_average_x_estimate['right'],
            1
        )

        self.is_sketchy_normalizer = not validation_was_successful
        print('boop')

    def normalize_estimates(self, raw_estimates):
        normalized_estimates = []
        for re in raw_estimates:
            rx = re['x']
            a = None
            b = None
            if rx < self.center_mapping[0]:
                a = self.left_mapping
                b = self.center_mapping
            else:
                a = self.center_mapping
                b = self.right_mapping
            normalized_estimates.append({
                'x': interpolate_with(rx, a[0], a[1], b[0], b[1]),
                't': re['t']
            })
        return normalized_estimates
