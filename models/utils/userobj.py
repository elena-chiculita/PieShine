class UserObj(object):
    """
    Inherited by classes with a collection of objects (Lights, Group, Groups)
    designed to act like a dictionary stored in _obj.
    """

    def __getitem__(self, key):
        return self._obj[key]

    def __setitem__(self, key, value):
        self._obj[key] = value

    def __len__(self):
        return len(self._obj)

    def set_obj(self, obj):
        self._obj = obj

    def values(self):
        return self._obj.values()

    def keys(self):
        return self._obj.keys()

    def items(self):
        return self._obj.items()

    def pop(self, key):
        return self._obj.pop(key)
