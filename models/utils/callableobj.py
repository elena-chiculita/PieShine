class CallableObj(object):
    """
    Inherited by classes with a collection of methods added at run-time (Lights, Group), stored in _method_list,
    designed to execute a method foreach light associated (DimmableLight, ColorLight, ExtendedColorLight),
    if that light supports the method.
    """

    def __init__(self, method_list):
        self._method_list = method_list

    def __call__(self, *args, **kwargs):
        [method(*args, **kwargs) for method in self._method_list]
