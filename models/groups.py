import time
from models.utils.comms import Comms
from models.utils.userobj import UserObj
from models.utils.callableobj import CallableObj
from models.utils.testobj import TestObj
from models.lights import Lights, REFRESH_TIMEOUT


class Group(UserObj, TestObj):
    """
    Model of a Philips hue lights group.
    Control all lights from the group.

    Contains a dictionary of all the light objects in the group indexed by the light names.
    Also you can address each light from the group as a member of this instance.

    Properties:
        name - Unique name of the group.
        lights - List of light ids (list of Light.id) from this group
        type - Type of the group ('LightGroup' - LightGroup class or 'Room' - RoomGroup class).
        state - Tell if all lights are On/Off and also if at least one light is On/Off
        action - Get On/Off state, brightness and alert settings of the group
    """

    def __init__(self, comms, id, lights=None):
        assert(isinstance(comms, Comms))
        self._comms = comms
        self.id = id
        self.__data = self._refresh()
        self.refresh_time = time.time()

        # lights is a dictionary of light objects from the setup (Lights() instance) indexed after light names
        if lights:
            assert (isinstance(lights, Lights))
            # each group will have a dictionary formed by the lights associated, indexed by light name
            self.set_obj({light.name: light for light in lights.values() if light.id in self.lights})

            # in order to control all lights from this group get the all parameters that can be set
            method_names = []
            # for each light in the setup
            for light in lights.values():
                # choose only lights from this group
                if light.id in self.lights:
                    # each light name from this group becomes a member of this instance,
                    # with the proper object associated
                    setattr(self, light._adapt_name(), light)

                    for method_name in dir(light):
                        # get all methods
                        if callable(getattr(light, method_name)) and not method_name.startswith('_'):
                            # and keep only those which are not private
                            method_names.append(method_name)

            # for each method
            for method_name in set(method_names):
                methods = []
                # for each light in the setup
                for light in lights.values():
                    # choose lights from the groups only
                    if light.id in self.lights:
                        # if the light supports this setting (i.e. cannot call set_color() for white lights, etc.)
                        if method_name in dir(light):
                            # get the method object
                            methods.append(getattr(light, method_name))
                # Each method will be called for each light in the group.
                # If a method does not apply to all lights in the group,
                # it will be called only for those lights that it can be applied to.
                # Basically when calling bridge.groups.Living.turn_on() this will execute for all lights in the group,
                # like calling bridge.groups.Living.LivingMain.turn_on(), bridge.groups.Living.LivingTwo.turn_on(), etc.
                setattr(self, method_name, CallableObj(methods))

    def __repr__(self):
        return "".join(light.__repr__() + '\n' for light in self.values())

    @property
    def _data(self):
        # perform GET at minimum 5s
        if time.time() - self.refresh_time >= REFRESH_TIMEOUT:
            self.__data = self._refresh()
            self.refresh_time = time.time()
        return self.__data

    @property
    def name(self):
        return self._data['name']

    @property
    def lights(self):
        return self._data['lights']

    @property
    def type(self):
        return self._data['type']

    @property
    def state(self):
        return self._data['state']

    @property
    def action(self):
        return self._data['action']

    @classmethod
    def _scan(cls, comms, type=None, lights=None):
        """
        Scan for a given group type.

        :param comms: Comms instance to communicate with the bridge
        :param type: Type of the group
        :param lights: Dictionary of light objects from the setup, indexed after light names (Lights() instance).
                       Each Group instance will add its lights based on self.lights and each Light.id from lights.
        :return: List of groups filtered after type parameter, or all groups if type is None.
        """

        d = comms.get('groups/')
        group_ids = []
        for key, value in d.items():
            if (type is None) or (value['type'] == type):
                group_ids.append(key)
        return [cls(comms, group_id, lights) for group_id in group_ids]

    def _adapt_name(self):
        return self.name.replace(' ', '')

    def _refresh(self):
        return self._comms.get('groups/' + str(self.id))


class RoomGroup(Group):
    """
    Model of a Philips hue lights 'Room' group.

    Contains all properties from Group and also:
        class_ - The category of room type. See Philips documentation for allowed values.
    """

    @property
    def class_(self):
        return self._data['class']

    @classmethod
    def _scan(cls, comms, lights=None):
        """
        Get a list of all 'Room' groups type from the setup.
        """

        return super(RoomGroup, cls)._scan(comms, 'Room', lights)


class LightGroup(Group):
    """
    Model of a Philips hue lights 'LightGroup' group.

    Contains all properties from Group and also:
        recycle - See Philips documentation for this one.
    """

    @property
    def recycle(self):
        return self._data['recycle']

    @classmethod
    def _scan(cls, comms, lights=None):
        """
        Get a list of all 'LightGroup' groups type from the setup.
        """

        return super(LightGroup, cls)._scan(comms, 'LightGroup', lights)


class Groups(UserObj):
    """
    Control all groups.

    Contains a dictionary of all the group objects in the setup indexed by the group names.
    Also you can address each group as a member of this instance.
    """

    def __init__(self, comms, lights=None):
        # get a list with each type of group
        room_groups = RoomGroup._scan(comms, lights)
        custom_groups = LightGroup._scan(comms, lights)
        all_groups = room_groups + custom_groups
        # and build the dictionary of groups indexed by group name
        self.set_obj({group.name: group for group in all_groups})
        # each group name becomes a member of this instance with the proper object associated
        [setattr(self, group._adapt_name(), group) for group in all_groups]

    def __repr__(self):
        return "".join('(' + str(group.id) + ') * ' + group.name + ' (' + group.type + ') *** ' + ', '.join(
            [light.name for light in group.values()]) + '\n' for group in self.values())

    def _add_group(self, comms, id, lights):
        # add an instance for the new group
        group = LightGroup(comms, id, lights)
        # and add it to the dictionary of groups indexed by group name
        self[group.name] = group
        # this group name becomes another member of this instance with the group object associated
        setattr(self, group._adapt_name(), group)

    def _delete_group(self, id):
        # get the group to be deleted
        for group in self.values():
            if group.id == str(id):
                key = group.name
                # delete the member associated with this group name
                delattr(self, group._adapt_name())
                # delete the instance
                del group
        # delete the group from the dictionary
        self.pop(key)
