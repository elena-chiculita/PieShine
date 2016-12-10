import time
from models.utils.comms import Comms
from models.utils.userobj import UserObj
from models.utils.callableobj import CallableObj
from models.utils.testobj import TestObj
from models.utils.color import Gamut


REFRESH_TIMEOUT = 5

# Associate a model id with a gamut.
ModelsGamut = {
    'LCT001': 'B',
    'LCT002': 'B',
    'LCT003': 'B',
    'LCT007': 'B',
    'LCT010': 'C',
    'LCT011': 'C',
    'LCT014': 'C',
    'LLC006': 'A',
    'LLC007': 'A',
    'LLC010': 'A',
    'LLC011': 'A',
    'LLC012': 'A',
    'LLC013': 'A',
    'LLC020': 'C',
    'LMM001': 'B',
    'LST001': 'A',
    'LST002': 'C'
}

# coordinates for each gamut
gamut_A_coords = {
    'red': {'x': 0.704, 'y': 0.296, 'hue': 0},
    'green': {'x': 0.2151, 'y': 0.7106, 'hue': 100},
    'blue': {'x': 0.138, 'y': 0.08, 'hue': 184},
    'name': 'A'
}

gamut_B_coords = {
    'red': {'x': 0.675, 'y': 0.322, 'hue': 0},
    'green': {'x': 0.409, 'y': 0.518, 'hue': 100},
    'blue': {'x': 0.167, 'y': 0.04, 'hue': 184},
    'name': 'B'
}

gamut_C_coords = {
    'red': {'x': 0.692, 'y': 0.308, 'hue': 0},
    'green': {'x': 0.17, 'y': 0.7, 'hue': 100},
    'blue': {'x': 0.153, 'y': 0.048, 'hue': 184},
    'name': 'C'
}

# instantiate each gamut: A, B and C
gamutA = Gamut(gamut_A_coords['name'],
               gamut_A_coords['red']['x'],
               gamut_A_coords['red']['y'],
               gamut_A_coords['green']['x'],
               gamut_A_coords['green']['y'],
               gamut_A_coords['blue']['x'],
               gamut_A_coords['blue']['y'])

gamutB = Gamut(gamut_B_coords['name'],
               gamut_B_coords['red']['x'],
               gamut_B_coords['red']['y'],
               gamut_B_coords['green']['x'],
               gamut_B_coords['green']['y'],
               gamut_B_coords['blue']['x'],
               gamut_B_coords['blue']['y'])

gamutC = Gamut(gamut_C_coords['name'],
               gamut_C_coords['red']['x'],
               gamut_C_coords['red']['y'],
               gamut_C_coords['green']['x'],
               gamut_C_coords['green']['y'],
               gamut_C_coords['blue']['x'],
               gamut_C_coords['blue']['y'])


def get_gamut_by_name(name):
    """
    Get the gamut object corresponding to gamut 'name'

    :param name: The Gamut name.
    :return: The gamut object (gamutA, gamutB, gamutC) corresponding to the given gamut name ('A', 'B' or 'C') or None.
    """

    if name == 'A':
        return gamutA
    elif name == 'B':
        return gamutB
    elif name == 'C':
        return gamutC
    else:
        return None


class Light(TestObj):
    """
    Model of a Philips hue light.

    Properties:
        name - Unique name of the light.
            on - True/False if the light is on or off.
            bri - Brightness of the light (minimum = 1, maximum = 255)
            alert - One of the following value:
                'none' - Stop performing an alert effect.
                'select' - Make the light blink once.
                'lselect' - Make the light blink for 15 seconds or until an alert 'none' is received.
        reachable - True/False if the light bulb is reachable or not
        type - white ('Dimmable light') or colored ('Color light' or 'Extended color light')
        model_id - Model id of the light (see ModelsGamut for model-gamut association for colored lights)
        manufacturer_name - Manufacturer name.
        unique_id - MAC address of the light.
        sw_version - Software version running on the light.
    """

    def __init__(self, comms, id):
        assert (isinstance(comms, Comms))
        self._comms = comms
        self.id = id
        self.__data = self._refresh()
        self.refresh_time = time.time()

        # for colored light bulbs identify the gamut according to its model id
        if self.model_id in ModelsGamut:
            self.gamut = get_gamut_by_name(ModelsGamut[self.model_id])
        else:
            self.gamut = None

    def __repr__(self):
        return '(' + self.id + ') * ' + self.name + ' * ' + ('On' if self.on else 'Off') + ' * bri = ' + str(self.bri)

    @property
    def _data(self, refresh=False):
        # perform GET at minimum 5s
        if refresh or (time.time() - self.refresh_time >= REFRESH_TIMEOUT):
            self.__data = self._refresh()
            self.refresh_time = time.time()
        return self.__data

    @property
    def name(self):
        return self._data['name']

    @property
    def on(self):
        return self._data['state']['on']

    @property
    def bri(self):
        return self._data['state']['bri']

    @property
    def alert(self):
        return self._data['state']['alert']

    @property
    def reachable(self):
        return self._data['state']['reachable']

    @property
    def type(self):
        return self._data['type']

    @property
    def model_id(self):
        return self._data['modelid']

    @property
    def manufacturer_name(self):
        return self._data['manufacturername']

    @property
    def unique_id(self):
        return self._data['uniqueid']

    @property
    def sw_version(self):
        return self._data['swversion']

    @classmethod
    def _scan(cls, comms, color=None):
        """
        Scan for a given light type.

        :param comms: Comms instance to communicate with the bridge
        :param color: Type of light bulb:
                      DimmableLight = white light
                      ColorLight = colored light
                      ExtendedColorLight = same as ColorLight, but color temperature can also be set)
        :return: List of lights filtered after color parameter, or all lights if color is None.
        """

        light_ids = []
        d = comms.get('lights/')
        [light_ids.append(key) for key, value in d.items() if (color is None) or (value['type'] == color)]
        return [cls(comms, light_id) for light_id in light_ids]

    def _adapt_name(self):
        return self.name.replace(' ', '')

    def _refresh(self):
        return self._comms.get('lights/' + str(self.id))

    def _force_refresh(self):
        self.refresh_time = time.time() - REFRESH_TIMEOUT

    def turn_on(self):
        self._comms.put('lights/' + str(self.id) + '/state', '{"on":true}')

    def turn_off(self):
        self._comms.put('lights/' + str(self.id) + '/state', '{"on":false}')

    def set_bri(self, bri):
        self._comms.put('lights/' + str(self.id) + '/state', '{"bri":' + str(bri) + '}')

    def set_alert(self, alert):
        self._comms.put('lights/' + str(self.id) + '/state', '{"alert":"' + str(alert) + '"}')


class DimmableLight(Light):
    """
    Model of a white Philips hue light (same properties as a Light instance).
    """

    @classmethod
    def _scan(cls, comms, color='Dimmable light'):
        """
        Get a list of all white light objects from the setup.
        """

        return super(DimmableLight, cls)._scan(comms, color)


class ColorLight(Light):
    """
    Model of a colored Philips hue light.

    Contains all properties from Light and also:
        hue - Hue of the light (minimum = 0, maximum = 65535, red = 0 or 65535, green = 25500, blue = 46920).
        sat - Saturation of the light (minimum = 0 = white, maximum = 254).
        effect - One of the following:
            'colorloop' - Puts the lights in a color looping mode until it is stopped by sending effect 'none'
            'none' - Stop performing 'colorloop' effect
        xy - Coordinates in CIE color space.
             List of 2 elements, first x and second y, both float between 0 and 1.
             If coordinates are outside the light's supported gamut - see ModelsGamut -
             these will pe approximated to coordinates inside the said gamut).
        colormode - Identify the light color mode:
            'hs' - set from hue and sat
            'xy' - set from 'xy'
    """

    def __repr__(self):
        return super(ColorLight, self).__repr__() + ' * Gamut ' + str(self.gamut.name) + ' [x,y] = ' + str(self.xy) + ' * sat = ' + str(
            self.sat) + ' * hue = ' + str(self.hue)

    @property
    def hue(self):
        return self._data['state']['hue']

    @property
    def sat(self):
        return self._data['state']['sat']

    @property
    def effect(self):
        return self._data['state']['effect']

    @property
    def xy(self):
        return self._data['state']['xy']

    @property
    def colormode(self):
        return self._data['state']['colormode']

    @classmethod
    def _scan(cls, comms, color='Color light'):
        """
        Get a list of all colored light (except the ones that support color temperature setting) objects from the setup.
        """

        return super(ColorLight, cls)._scan(comms, color)

    def set_hue(self, hue):
        self._comms.put('lights/' + str(self.id) + '/state', '{"hue":' + str(hue) + '}')

    def set_sat(self, sat):
        self._comms.put('lights/' + str(self.id) + '/state', '{"sat":' + str(sat) + '}')

    def set_effect(self, effect):
        self._comms.put('lights/' + str(self.id) + '/state', '{"effect":"' + str(effect) + '"}')

    def set_xy(self, x, y):
        self._comms.put('lights/' + str(self.id) + '/state', '{"xy":[' + str(x) + ',' + str(y) + ']' + '}')

    def set_color(self, red, green, blue):
        if self.gamut is None:
            print('Model id not found. Cannot set color !!!')
            return

        x, y, bri = self.gamut.get_xy_and_bri_from_rgb(red, green, blue)
        self.set_xy(x, y)
        self.set_bri(bri)


class ExtendedColorLight(ColorLight):
    """
    Model of a colored Philips hue light.

    Contains all properties from Light, ColorLight and also:
        ct - The Mired Color temperature of the light (minimum = 153 (6500K), maximum = 500 (2000K)).
        colormode - Identify the light color mode:
            'hs' - set from hue and sat
            'xy' - set from 'xy'
            'ct' - color temperature
    """

    def __repr__(self):
        return super(ExtendedColorLight, self).__repr__() + ' * ct = ' + str(self.ct)

    @property
    def ct(self):
        return self._data['state']['ct']

    @classmethod
    def _scan(cls, comms, color='Extended color light'):
        """
        Get a list of all colored light (that support color temperature setting) objects from the setup.
        """
        return super(ExtendedColorLight, cls)._scan(comms, color)

    def set_ct(self, ct):
        self._comms.put('lights/' + str(self.id) + '/state', '{"ct":' + str(ct) + '}')


class Lights(UserObj, TestObj):
    """
    Control all lights.

    Contains a dictionary of all the light objects in the setup indexed by the light names.
    Also you can access each light as a member of this instance.
    """

    def __init__(self, comms):
        # get a list with each type of light
        dimmable_lights = DimmableLight._scan(comms)
        color_lights = ColorLight._scan(comms)
        extended_color_lights = ExtendedColorLight._scan(comms)
        all_lights = dimmable_lights + color_lights + extended_color_lights
        # and build the dictionary of lights indexed by light name
        self.set_obj({light.name: light for light in all_lights})
        # each light name becomes a member of this instance with the proper object associated
        [setattr(self, light._adapt_name(), light) for light in all_lights]

        # in order to control all lights get all parameters that can be set
        method_names = []
        for light in all_lights:
            # for each light
            for method_name in dir(light):
                # get all methods
                if callable(getattr(light, method_name)) and not method_name.startswith('_'):
                    # and keep only those which are not private
                    method_names.append(method_name)

        # for each method
        for method_name in set(method_names):
            methods = []
            # for each light in the setup
            for light in all_lights:
                # if the light supports this setting (i.e. cannot call set_color() for white lights, etc.)
                if method_name in dir(light):
                    # get the method object
                    methods.append(getattr(light, method_name))
            # Each method will be called for each light in the setup.
            # If a method does not apply to all lights in the setup,
            # it will be called only for those lights that it can be applied to.
            # Basically when calling bridge.lights.turn_on() this will execute for all lights in the setup,
            # like calling bridge.lights.LivingMain.turn_on(), bridge.lights.Stairs.turn_on(), etc.
            setattr(self, method_name, CallableObj(methods))

    def __repr__(self):
        return "".join(str(light) + '\n' for light in self.values())
