from sympy.core.core import BasicMeta
from sympy.core.assumptions import ManagedProperties
from sympy.core.basic import Basic
from sympy.core.sympify import sympify
from sympy.core.decorators import deprecated
from sympy.core.cache import cacheit

class FunctionClass(ManagedProperties):
    """
    Base class for function classes. FunctionClass is a subclass of type.

    Use Function('<function name>' [ , signature ]) to create
    undefined function classes.
    """
    __metaclass__ = BasicMeta

    _new = type.__new__

    def __repr__(cls):
        return cls.__name__

    @deprecated
    def __contains__(self, obj):
        return (self == obj)


class Application(Basic):
    """
    Base class for applied functions.

    Instances of Application represent the result of applying an application of
    any type to any object.
    """
    __metaclass__ = FunctionClass
    __slots__ = []

    is_Function = True

    nargs = None

    @cacheit
    def __new__(cls, *args, **options):
        args = map(sympify, args)
        evaluate = options.pop('evaluate', True)
        if options:
            raise ValueError("Unknown options: %s" % options)

        if evaluate:
            evaluated = cls.eval(*args)
            if evaluated is not None:
                return evaluated
        return super(Application, cls).__new__(cls, *args)

    @classmethod
    def eval(cls, *args):
        """
        Returns a canonical form of cls applied to arguments args.

        The eval() method is called when the class cls is about to be
        instantiated and it should return either some simplified instance
        (possible of some other class), or if the class cls should be
        unmodified, return None.

        Examples of eval() for the function "sign"
        ---------------------------------------------

        @classmethod
        def eval(cls, arg):
            if arg is S.NaN:
                return S.NaN
            if arg is S.Zero: return S.Zero
            if arg.is_positive: return S.One
            if arg.is_negative: return S.NegativeOne
            if isinstance(arg, C.Mul):
                coeff, terms = arg.as_coeff_Mul(rational=True)
                if coeff is not S.One:
                    return cls(coeff) * cls(terms)

        """
        return

    @property
    def func(self):
        return self.__class__

    def _eval_subs(self, old, new):
        from sympy.core.function import Lambda
        if (isinstance(old, FunctionClass) and isinstance(new, (FunctionClass, Lambda)) and
                old == self.func and
                (self.nargs == new.nargs or not new.nargs or
                    isinstance(new.nargs, tuple) and self.nargs in new.nargs)):
            return new(*self.args)

    @deprecated
    def __contains__(self, obj):
        if self.func == obj:
            return True
        return super(Application, self).__contains__(obj)
