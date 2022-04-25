class Normalizer:
    def __init__(self, center_x, results):
        delta_width = round(center_x * 2 / 3)
        first_center_result = results[0]
        last_center_result = results[-1]
        top_left_result = [
            r for r in results if r['step'] == { 'x': -1, 'y': -1 }
        ][0]
        bot_left_result = [
            r for r in results if r['step'] == { 'x': -1, 'y': 1 }
        ][0]
        top_right_result = [
            r for r in results if r['step'] == { 'x': 1, 'y': -1 }
        ][0]
        bot_right_result = [
            r for r in results if r['step'] == { 'x': 1, 'y': 1 }
        ][0]
        real_left_validation_x = center_x - delta_width
        real_right_validation_x = center_x + delta_width

        print('real_left_x: %d; top_left_x: %d, bot_left_x: %d' % (
            real_left_validation_x,
            top_left_result['avgX'],
            bot_left_result['avgX']
        ))
        print('real_right_x: %d; top_right_x: %d, bot_right_x: %d' % (
            real_right_validation_x,
            top_right_result['avgX'],
            bot_right_result['avgX']
        ))
        print('real_center_x: %d; first_center_x: %d, second_center_x: %d' % (
            center_x,
            first_center_result['avgX'],
            last_center_result['avgX']
        ))
        left_estimation_goes_beyond_center_estimation = \
            top_left_result['avgX'] > first_center_result['avgX'] or \
            top_left_result['avgX'] > last_center_result['avgX'] or \
            bot_left_result['avgX'] > first_center_result['avgX'] or \
            bot_left_result['avgX'] > last_center_result['avgX']
        right_estimation_goes_beyond_center_estimation = \
            top_right_result['avgX'] < first_center_result['avgX'] or \
            top_right_result['avgX'] < last_center_result['avgX'] or \
            bot_right_result['avgX'] < first_center_result['avgX'] or \
            bot_right_result['avgX'] < last_center_result['avgX']
        print(
            'left_estimation_goes_beyond_center_estimation:',
            left_estimation_goes_beyond_center_estimation
        )
        print(
            'right_estimation_goes_beyond_center_estimation:',
            right_estimation_goes_beyond_center_estimation
        )

        self.validation_was_sketchy = \
            left_estimation_goes_beyond_center_estimation or \
            right_estimation_goes_beyond_center_estimation
