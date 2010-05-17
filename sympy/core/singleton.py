"""Singleton mechanism"""

from core import BasicMeta, Registry
from sympify import sympify
from basic import Atom

class SingletonRegistry(Registry):
    """
    A map between singleton classes and the corresponding instances.
    E.g. S.Exp == C.Exp()
    """
    __slots__ = []

    __call__ = staticmethod(sympify)

    def __repr__(self):
        return "S"

S = SingletonRegistry()

class SingletonMeta(BasicMeta):
    """Metaclass for all singletons
    """
    def __init__(cls, *args, **kw):
        BasicMeta.__init__(cls, *args, **kw)
        setattr(cls.__registry__, cls.__name__, cls())


class Singleton(Atom):
    __metaclass__ = SingletonMeta
    __slots__ = []
    __registry__ = S

    def __new__(cls):
        try:
            obj = getattr(cls.__registry__, cls.__name__)
        except AttributeError:
            obj = Atom.__new__(cls, *(), **{})
        return obj

    def __getnewargs__(self):
        """Pickling support."""
        return ()


