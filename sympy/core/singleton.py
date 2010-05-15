"""Singleton mechanism"""

from core import BasicMeta, C
from sympify import sympify
from basic import Basic

class SingletonMeta(BasicMeta):
    """Metaclass for all singletons

       All singleton classes should put this into their __metaclass__, and
       _not_ to define __new__

       example:

       class Zero(Integer):
           __metaclass__ = SingletonMeta

           p = 0
           q = 1
    """

    def __init__(cls, *args, **kw):
        BasicMeta.__init__(cls, *args, **kw)


class Singleton(Basic):
    __metaclass__ = SingletonMeta
    __slots__ = []

    def __new__(cls):
        try:
            obj = getattr(SingletonFactory, cls.__name__)

        except AttributeError:
            obj = Basic.__new__(cls, *(), **{})
            setattr(SingletonFactory, cls.__name__, obj)

        return obj

    def __getnewargs__(self):
        """Pickling support."""
        return ()

class SingletonFactory:
    """
    A map between singleton classes and the corresponding instances.
    E.g. S.Exp == C.Exp()
    """

    def __getattr__(self, clsname):
        if clsname == "__repr__":
            return lambda: "S"

        cls = getattr(C, clsname)
        assert issubclass(cls, Singleton)
        obj = cls()

        # store found object in own __dict__, so the next lookups will be
        # serviced without entering __getattr__, and so will be fast
        setattr(self, clsname, obj)
        return obj

S = SingletonFactory()

S.__call__ = sympify
