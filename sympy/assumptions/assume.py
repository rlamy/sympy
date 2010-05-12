# doctests are disabled because of issue #1521
from sympy.core import  Symbol
from sympy.core.relational import Relational
from sympy.logic.boolalg import Boolean, Not

class AssumptionsContext(set):
    """Set representing assumptions.

    This is used to represent global assumptions, but you can also use this
    class to create your own local assumptions contexts. It is basically a thin
    wrapper to Python's set, so see its documentation for advanced usage.

    Examples:
        >>> from sympy import global_assumptions, Assume, Q
        >>> global_assumptions
        AssumptionsContext()
        >>> from sympy.abc import x
        >>> global_assumptions.add(Assume(x, Q.real))
        >>> global_assumptions
        AssumptionsContext([Q.real(x)])
        >>> global_assumptions.remove(Assume(x, Q.real))
        >>> global_assumptions
        AssumptionsContext()
        >>> global_assumptions.clear()

    """

    def add(self, *assumptions):
        """Add an assumption."""
        for a in assumptions:
            assert isinstance(a, ApplyPredicate), 'can only store instances of Assume'
            super(AssumptionsContext, self).add(a)

global_assumptions = AssumptionsContext()

def Assume(expr, predicate=None, value=True):
    """New-style assumptions.

    >>> from sympy import Assume, Q
    >>> from sympy.abc import x
    >>> Assume(x, Q.integer)
    Q.integer(x)
    >>> Assume(x, Q.integer, False)
    Not(Q.integer(x))
    >>> Assume( x > 1 )
    Q.is_true(1 < x)

    """
    from sympy import Q
    if predicate is None:
        predicate = Q.is_true
    elif not isinstance(predicate, Predicate):
        key = str(predicate)
        try:
            predicate = getattr(Q, key)
        except AttributeError:
            predicate = Predicate(key)
    if value:
        return ApplyPredicate(predicate, expr)
    else:
        return Not(ApplyPredicate(predicate, expr))

class ApplyPredicate(Boolean):
    """New-style assumptions.

    >>> from sympy import Assume, Q
    >>> from sympy.abc import x
    >>> Q.integer(x)
    Q.integer(x)

    """
    __slots__ = []

    def __new__(cls, predicate, arg):
        return Boolean.__new__(cls, predicate, arg)

    is_Atom = True # do not attempt to decompose this

    @property
    def arg(self):
        """
        Return the expression used by this assumption.

        Examples:
            >>> from sympy import Assume, Q
            >>> from sympy.abc import x
            >>> a = Assume(x+1, Q.integer)
            >>> a.arg
            1 + x

        """
        return self._args[1]

    @property
    def args(self):
        return self._args[1:]

    @property
    def func(self):
        """
        Return the key used by this assumption.
        It is a string, e.g. 'integer', 'rational', etc.

        Examples:
            >>> from sympy import Assume, Q
            >>> from sympy.abc import x
            >>> a = Assume(x, Q.integer)
            >>> a.func
            'integer'

        """
        return self._args[0]

    def __eq__(self, other):
        if type(other) == ApplyPredicate:
            return self._args == other._args
        return False

def eliminate_assume(expr, symbol=None):
    """
    Convert an expression with assumptions to an equivalent with all assumptions
    replaced by symbols.

    Assume(x, integer=True) --> integer
    Assume(x, integer=False) --> ~integer

    Examples:
        >>> from sympy.assumptions.assume import eliminate_assume
        >>> from sympy import Assume, Q
        >>> from sympy.abc import x
        >>> eliminate_assume(Assume(x, Q.positive))
        Q.positive
        >>> eliminate_assume(Assume(x, Q.positive, False))
        Not(Q.positive)

    """
    if expr.__class__ is ApplyPredicate:
        if symbol is not None:
            if not expr.arg.has(symbol):
                return
        return expr.func
    return expr.func(*[eliminate_assume(arg, symbol) for arg in expr.args])

class Predicate(Boolean):

    is_Atom = True

    def __new__(cls, name, handlers=None):
        obj = Boolean.__new__(cls)
        obj.name = name
        obj.handlers = handlers or []
        return obj

    def _hashable_content(self):
        return (self.name,)

    def __getnewargs__(self):
        return (self.name,)

    def __call__(self, expr):
        return ApplyPredicate(self, expr)

    def add_handler(self, handler):
        self.handlers.append(handler)

    def remove_handler(self, handler):
        self.handlers.remove(handler)
