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

        self.is_sketchy_normalizer = not validation_was_successful
        print('boop')
