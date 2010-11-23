"""Generic functions"""
from inspect import getargspec, getmro

class GenericFunction(object):
    def __init__(self):
        self.implementation = {}
        self._cache = {}

    def __call__(self, *args, **kwargs):
        arg = args[0]
        cls = arg.__class__
        try:
            return self._cache[cls](*args, **kwargs)
        except IndexError:
            for scls in arg.__class__.__mro__:
                if scls in self._cache:
                    ret = self._cache[scls]
                    self._cache[cls] = ret
                    return ret
            raise TypeError

class Signature(object):
    def __init__(self, func):
        args, self.varargs, self.keywords, default = getargspec(func)
        default = default or []
        n = len(default)
        self.posargs = args[:len(args)-n]
        self.kwargs = dict(zip(args[len(args)-n:], default))

    def assert_matches(self, other):
        """Test whether ``self`` is a valid signature for an implementation of a
        generic function with signature ``other``."""
        if len(self.posargs) != len(other.posargs):
            raise ValueError("Wrong number of positional args: %s instead of %s"
                    % (self.posargs, other.posargs))
        if other.varargs and not self.varargs:
            raise ValueError("Implementation must accept any positional args")
        if other.keywords and not self.keywords:
            raise ValueError("Implementation must accept any kwargs")
        if not self.keywords and other.kwargs.items() not in self.kwargs.items():
            raise ValueError("Kwarg mismatch: %s instead of %s"
                    % (self.kwargs, other.kwargs))


class Dispatcher(object):
    def __init__(self, func):
        self.func = func
        self.signature = Signature(func)
        self.registry = {object: func}
        self.cache = {}

    def __getitem__(self, cls):
        try:
            return self.cache[cls]
        except KeyError:
            if not self.cache:
                self.cache = dict(self.registry)
            for scls in getmro(cls):
                if scls in self.cache:
                    ret = self.cache[scls]
                    self.cache[cls] = ret
                    return ret
            self.cache[cls] = self.func
            return self.func

    def __setitem__(self, cls, func):
        Signature(func).assert_matches(self.signature)
        self.registry[cls] = func
        self.cache = {}

    def __delitem__(self, cls):
        del self.registry[cls]
        self.cache = {}

def generic(func):
    """
    Make a generic function
    """
    dispatcher = Dispatcher(func)
    def dispatch(*args, **kwargs):
        try:
            cls = args[0].__class__
        except AttributeError:  #a is probably an old-style class object
            cls = type(args[0])
        return dispatcher[cls](*args, **kwargs)

    dispatch.__doc__ = func.__doc__
    dispatch.__name__ = func.__name__
    dispatch.implementation = dispatcher

    def when(*classes):
        """
        Add a specialised implementation of the parent function for instances of `cls`
        """
        def decorate(func):
            for cls in classes:
                dispatcher[cls] = func
            return func
        return decorate
    dispatch.when = when

    return dispatch
