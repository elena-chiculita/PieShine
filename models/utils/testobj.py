import time
from models.utils.callableobj import CallableObj


def assert_equal(a, b, err_msg):
    if a != b:
        print('FAIL : ' + err_msg)
    else:
        print('PASS : ' + err_msg)


class TestObj(object):
    """"
    Provides testing for all types of light parameters.
    """

    def _test(self):
        # supported settings for all types of lights
        test_methods = [
            {'method': 'turn_on', 'params': None, 'vars': ['on'], 'expected_values': [True]},
            {'method': 'turn_off', 'params': None, 'vars': ['on'], 'expected_values': [False]},
            {'method': 'turn_on', 'params': None, 'vars': ['on'], 'expected_values': [True]},
            {'method': 'set_bri', 'params': [1], 'vars': ['bri'], 'expected_values': [1]},
            {'method': 'set_bri', 'params': [150], 'vars': ['bri'], 'expected_values': [150]},
            {'method': 'set_bri', 'params': [255], 'vars': ['bri'], 'expected_values': [254]},
            {'method': 'set_alert', 'params': ['lselect'], 'vars': ['alert'], 'expected_values': ['lselect'],
             'sleep':5},
            {'method': 'set_alert', 'params': ['none'], 'vars': ['alert'], 'expected_values': ['none']},
            {'method': 'set_effect', 'params': ['colorloop'], 'vars': ['effect'], 'expected_values': ['colorloop'],
             'sleep': 10},
            {'method': 'set_effect', 'params': ['none'], 'vars': ['effect'], 'expected_values': ['none']},
            {'method': 'set_hue', 'params': [0], 'vars': ['hue'], 'expected_values': [0]},
            {'method': 'set_hue', 'params': [30000], 'vars': ['hue'], 'expected_values': [30000]},
            {'method': 'set_hue', 'params': [65535], 'vars': ['hue'], 'expected_values': [65535]},
            {'method': 'set_sat', 'params': [0], 'vars': ['sat'], 'expected_values': [0]},
            {'method': 'set_sat', 'params': [125], 'vars': ['sat'], 'expected_values': [125]},
            {'method': 'set_sat', 'params': [254], 'vars': ['sat'], 'expected_values': [254]},
            {'method': 'set_xy', 'params': [0.4, 0.4], 'vars': ['xy'], 'expected_values': [[0.4, 0.4]]},
            {'method': 'set_xy', 'params': [0.7, 0.7], 'vars': ['xy'], 'expected_values': [[0.7, 0.7]]},
            {'method': 'set_color', 'params': [255, 255, 255], 'vars': ['xy', 'bri'],
             'expected_values': [{'A': {'x': 0.3227, 'y': 0.329},
                                  'B': {'x': 0.3227, 'y': 0.329},
                                  'C': {'x': 0.3227, 'y': 0.329}},
                                 254]},
            {'method': 'set_color', 'params': [0, 0, 0], 'vars': ['xy', 'bri'],
             'expected_values': [{'A': {'x': 0.3227, 'y': 0.329},
                                  'B': {'x': 0.3227, 'y': 0.329},
                                  'C': {'x': 0.3227, 'y': 0.329}},
                                 1]},
            {'method': 'set_color', 'params': [200, 171, 196], 'vars': ['xy', 'bri'],
             'expected_values': [{'A': {'x': 0.3409, 'y': 0.2941},
                                  'B': {'x': 0.3409, 'y': 0.2941},
                                  'C': {'x': 0.3409, 'y': 0.2941}},
                                 117]},
            {'method': 'set_color', 'params': [37, 171, 186], 'vars': ['xy', 'bri'],
             'expected_values': [{'A': {'x': 0.1661, 'y': 0.3097},
                                  'B': {'x': 0.2745, 'y': 0.2523},
                                  'C': {'x': 0.1598, 'y': 0.3104}},
                                 76]},
            {'method': 'set_ct', 'params': [153], 'vars': ['ct'], 'expected_values': [153]},
            {'method': 'set_ct', 'params': [359], 'vars': ['ct'], 'expected_values': [359]},
            {'method': 'set_ct', 'params': [500], 'vars': ['ct'], 'expected_values': [500]}
        ]

        self.passed = self.failed = 0
        self.exec_time = time.time()

        for test_method in test_methods:
            method = test_method['method']
            # check if method was added at run-time (Lights and Group classes)
            if method in self.__dict__ and isinstance(getattr(self, method), CallableObj):
                # if so, 'self' is an instance of Lights or Group containing a dictionary of lights
                lights = self.values()
            # either if it is supported (DimmableLight, ColorLight or ExtendedColorLight classes)
            elif method in dir(self.__class__) and callable(getattr(self, method)):
                # if so, 'self' is an instance of DimmableLight, ColorLight or ExtendedColorLight
                lights = [self]
            # method is not supported
            else:
                continue

            # execute method
            params = test_method['params']
            if params is None:
                getattr(self, method)()
            else:
                getattr(self, method)(*params)

            # check each light
            for light in lights:
                # if the current setting is supported
                if method in dir(light):
                    # verify each expected param against its expected value
                    for i in range(len(test_method['vars'])):
                        var, value = test_method['vars'][i], test_method['expected_values'][i]
                        light._force_refresh()
                        # When setting the color 'xy' parameter along with 'bri' are being set, and
                        # the expected result for 'xy' depends on the light's gamut.
                        if (method == 'set_color') and (i == 0):
                            value = [test_method['expected_values'][i][light.gamut.name]['x'],
                                     test_method['expected_values'][i][light.gamut.name]['y']]
                        assert_equal(getattr(light, var), value,
                                     '%s : %s : %s : expected : %s , received : %s' % (
                                     light.name, method, var, str(value), str(getattr(light, var))))
                        if getattr(light, var) == value:
                            self.passed += 1
                        else:
                            self.failed += 1

            if 'sleep' in test_method:
                time.sleep(test_method['sleep'])
            else:
                time.sleep(0.5)

            # new row after each light/method
            if len(lights) > 1:
                print('')

        self.exec_time = time.time() - self.exec_time
        m, s = divmod(self.exec_time, 60)
        h, m = divmod(m, 60)
        print('======== PASSED = %d , FAILED = %d , TIME = %dmin:%02ds ========\n' % (self.passed, self.failed, m, s))
