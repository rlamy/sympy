from sympy.core import S, C, sympify, Function, Lambda
from sympy.core.singleton import Singleton
from sympy.core.symbol import Dummy

class IdentityFunction(Lambda):
    """The identity function

    >>> from sympy import Id, Symbol
    >>> x = Symbol('x')
    >>> Id(x)
    x
    """
    __metaclass__ = Singleton
    __slots__ = []
    nargs = 1
    def __new__(cls):
        x = C.Dummy('x')
        return Lambda([x], x)
Id = S.IdentityFunction

###############################################################################
############################# SQUARE ROOT FUNCTION ############################
###############################################################################

def sqrt(arg):
    # arg = sympify(arg) is handled by Pow
    return C.Pow(arg, S.Half)

###############################################################################
############################# MINIMUM and MAXIMUM #############################
###############################################################################

class Max(Function):

    nargs = 2

    @classmethod
    def eval(cls, x, y):
        """Return, if possible, the value from (a, b) that is >= the other.

        >>> from sympy import Max, Symbol
        >>> from sympy.abc import x
        >>> Max(x, -2)
        Max(x, -2)
        >>> _.subs(x, 3)
        3

        Assumptions are used to make the decision:

        >>> p = Symbol('p', positive=True)
        >>> Max(p, -2)
        p
        """

        if x == y:
            return x
        if x.is_Number and y.is_Number:
            return max(x, y)
        xy = x > y
        if isinstance(xy, bool):
            if xy:
                return x
            return y
        yx = y > x
        if isinstance(yx, bool):
            if yx:
                return y # never occurs?
            return x


class Min(Function):

    nargs = 2

    @classmethod
    def eval(cls, x, y):
        """Return, if possible, the value from (a, b) that is <= the other."""
        rv = Max(x, y)
        if rv == x:
            return y
        elif rv == y:
            return x
