"""Module for Sympy containers

    (Sympy objects that store other Sympy objects)

    The containers implemented in this module are subclassed to Basic.
    They are supposed to work seamlessly within the Sympy framework.
"""
from sympy.core.sympify import sympify
from sympy.core.basic import Basic
from sympy.core.multidimensional import vectorize
from sympy.core.core import BasicMeta
from sympy.core.cache import cacheit

class Tuple(Basic):
    """
    Wrapper around the builtin tuple object

    The Tuple is a subclass of Basic, so that it works well in the
    Sympy framework.  The wrapped tuple is available as self.args, but
    you can also access elements or slices with [:] syntax.

    >>> from sympy import symbols
    >>> from sympy.core.containers import Tuple
    >>> a, b, c, d = symbols('a b c d')
    >>> Tuple(a, b, c)[1:]
    Tuple(b, c)
    >>> Tuple(a, b, c).subs(a, d)
    Tuple(d, b, c)

    """

    def __getitem__(self,i):
        if isinstance(i,slice):
            indices = i.indices(len(self))
            return Tuple(*[self.args[i] for i in range(*indices)])
        return self.args[i]

    def __len__(self):
        return len(self.args)

    def __contains__(self, item):
        return item in self.args

    def __iter__(self):
        return iter(self.args)

    def __add__(self, other):
        if isinstance(other, Tuple):
            return Tuple(*(self.args + other.args))
        elif isinstance(other, tuple):
            return Tuple(*(self.args + other))
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Tuple):
            return Tuple(*(other.args + self.args))
        elif isinstance(other, tuple):
            return Tuple(*(other + self.args))
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Basic):
            return super(Tuple, self).__eq__(other)
        return self.args == other

    def __ne__(self, other):
        if isinstance(other, Basic):
            return super(Tuple, self).__ne__(other)
        return self.args != other

    def __hash__(self):
        return hash(self.args)


def tuple_wrapper(method):
    """
    Decorator that converts any tuple in the function arguments into a Tuple.

    The motivation for this is to provide simple user interfaces.  The user can
    call a function with regular tuples in the argument, and the wrapper will
    convert them to Tuples before handing them to the function.

    >>> from sympy.core.containers import tuple_wrapper, Tuple
    >>> def f(*args):
    ...    return args
    >>> g = tuple_wrapper(f)

    The decorated function g sees only the Tuple argument:

    >>> g(0, (1, 2), 3)
    (0, Tuple(1, 2), 3)

    """
    def wrap_tuples(*args, **kw_args):
        newargs=[]
        for arg in args:
            if type(arg) is tuple:
                newargs.append(Tuple(*arg))
            else:
                newargs.append(arg)
        return method(*newargs, **kw_args)
    return wrap_tuples


class ShortCircuit(Exception):
    pass

class LatticeOp(Basic):
    """
    Join/meet operations of an algebraic lattice[1].

    These binary operations are associative (op(op(a, b), c) = op(a, op(b, c))),
    commutative (op(a, b) = op(b, a)) and idempotent (op(a, a) = op(a) = a).
    Common examples are AND, OR, Union, Intersection, max or min. They have an
    identity element (op(identity, a) = a) and an absorbing element
    conventionally called zero (op(zero, a) = zero).

    This is an abstract base class, concrete derived classes must declare
    attributes zero and identity. All defining properties are then respected.

    >>> from sympy import Integer
    >>> from sympy.core.containers import LatticeOp
    >>> class my_join(LatticeOp):
    ...     zero = Integer(0)
    ...     identity = Integer(1)
    >>> my_join(2, 3) == my_join(3, 2)
    True
    >>> my_join(2, my_join(3, 4)) == my_join(2, 3, 4)
    True
    >>> my_join(0, 1, 4, 2, 3, 4)
    0
    >>> my_join(1, 2)
    2

    References:

    [1] - http://en.wikipedia.org/wiki/Lattice_(order)
    """

    is_commutative = True

    def __new__(cls, *args, **assumptions):
        args = (sympify(arg) for arg in args)
        try:
            _args = frozenset(cls._new_args_filter(args))
        except ShortCircuit:
            return cls.zero
        if not _args:
            return cls.identity
        elif len(_args) == 1:
            return set(_args).pop()
        else:
            obj = Basic.__new__(cls, _args, **assumptions)
            obj._argset = _args
            return obj

    @classmethod
    def _new_args_filter(cls, arg_sequence):
        """Generator filtering args"""
        for arg in arg_sequence:
            if arg == cls.zero:
                raise ShortCircuit(arg)
            elif arg == cls.identity:
                continue
            elif arg.func == cls:
                for x in arg.iter_basic_args():
                    yield x
            else:
                yield arg

    @classmethod
    def make_args(cls, expr):
        """
        Return a sequence of elements `args` such that cls(*args) == expr

        >>> from sympy import Symbol, Mul, Add
        >>> x, y = map(Symbol, 'xy')

        >>> Mul.make_args(x*y)
        (x, y)
        >>> Add.make_args(x*y)
        (x*y,)
        >>> set(Add.make_args(x*y + y)) == set([y, x*y])
        True

        """
        if isinstance(expr, cls):
            return expr._argset
        else:
            return frozenset([expr])

    @property
    def args(self):
        return tuple(self._argset)

    @staticmethod
    def _compare_pretty(a, b):
        return cmp(str(a), str(b))


class ApplicationClass(BasicMeta):
    """
    Base class for function classes. FunctionClass is a subclass of type.

    Use Function('<function name>' [ , signature ]) to create
    undefined function classes.
    """
    __metaclass__ = BasicMeta
    _new = type.__new__

    def __repr__(cls):
        return cls.__name__

    def __contains__(self, obj):
        return (self == obj)

class Application(Basic):
    """
    Base class for applied functions.

    Instances of Application represent the result of applying an application of
    any type to any object.
    """
    __metaclass__ = ApplicationClass
    __slots__ = []

    is_Function = True

    nargs = None

    @classmethod
    def _should_evalf(cls, arg):
        """
        Decide if the function should automatically evalf().
        By default (in this implementation), this happens if (and only if) the
        ARG is a floating point number.
        This function is used by __new__.
        """
        if arg.is_Real:
            return True
        if not arg.is_Add:
            return False
        re, im = arg.as_real_imag()
        return re.is_Real or im.is_Real

    @cacheit
    def __new__(cls, *args, **options):
        args = map(sympify, args)
        # these lines should be refactored
        for opt in ["nargs", "dummy", "comparable", "noncommutative", "commutative"]:
            if opt in options:
                del options[opt]
        # up to here.
        if not options.pop('evaluate', True):
            return super(Application, cls).__new__(cls, *args, **options)
        evaluated = cls.eval(*args)
        if evaluated is not None:
            return evaluated
        # Just undefined functions have nargs == None
        if not cls.nargs and hasattr(cls, 'undefined_Function'):
            r = super(Application, cls).__new__(cls, *args, **options)
            r.nargs = len(args)
            return r
        r = super(Application, cls).__new__(cls, *args, **options)
        if any([cls._should_evalf(a) for a in args]):
            return r.evalf()
        return r

    @classmethod
    def eval(cls, *args):
        """
        Returns a canonical form of cls applied to arguments args.

        The eval() method is called when the class cls is about to be
        instantiated and it should return either some simplified instance
        (possible of some other class), or if the class cls should be
        unmodified, return None.

        Example of eval() for the function "sign"
        ---------------------------------------------

        @classmethod
        def eval(cls, arg):
            if arg is S.NaN:
                return S.NaN
            if arg is S.Zero: return S.Zero
            if arg.is_positive: return S.One
            if arg.is_negative: return S.NegativeOne
            if isinstance(arg, C.Mul):
                coeff, terms = arg.as_coeff_mul()
                if coeff is not S.One:
                    return cls(coeff) * cls(arg._new_rawargs(*terms))

        """
        return

    @property
    def func(self):
        return self.__class__

    def _eval_subs(self, old, new):
        if self == old:
            return new
        elif old.is_Function and new.is_Function:
            if old == self.func:
                if self.nargs == new.nargs or not new.nargs:
                    return new(*self.args)
                # Written down as an elif to avoid a super-long line
                elif isinstance(new.nargs, tuple) and self.nargs in new.nargs:
                    return new(*self.args)
        return self.func(*[s.subs(old, new) for s in self.args])

    def __contains__(self, obj):
        if self.func == obj:
            return True
        return super(Application, self).__contains__(obj)
