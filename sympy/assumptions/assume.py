import inspect
from sympy.utilities.source import get_class
from sympy.logic.boolalg import Boolean

class AssumptionsContext(set):
    """Set representing assumptions.

    This is used to represent global assumptions, but you can also use this
    class to create your own local assumptions contexts. It is basically a thin
    wrapper to Python's set, so see its documentation for advanced usage.

    Examples
    ========

        >>> from sympy import global_assumptions, AppliedPredicate, Q
        >>> global_assumptions
        AssumptionsContext()
        >>> from sympy.abc import x
        >>> global_assumptions.add(Q.real(x))
        >>> global_assumptions
        AssumptionsContext([Q.real(x)])
        >>> global_assumptions.remove(Q.real(x))
        >>> global_assumptions
        AssumptionsContext()
        >>> global_assumptions.clear()

    """

    def add(self, *assumptions):
        """Add an assumption."""
        for a in assumptions:
            super(AssumptionsContext, self).add(a)

global_assumptions = AssumptionsContext()

class AppliedPredicate(Boolean):
    """The class of expressions resulting from applying a Predicate.

    >>> from sympy import Q, Symbol
    >>> x = Symbol('x')
    >>> Q.integer(x)
    Q.integer(x)
    >>> type(Q.integer(x))
    <class 'sympy.assumptions.assume.AppliedPredicate'>

    """
    __slots__ = []

    def __new__(cls, predicate, arg):
        return Boolean.__new__(cls, predicate, arg)

    is_Atom = True # do not attempt to decompose this

    @property
    def arg(self):
        """
        Return the expression used by this assumption.

        Examples
        ========

            >>> from sympy import Q, Symbol
            >>> x = Symbol('x')
            >>> a = Q.integer(x + 1)
            >>> a.arg
            x + 1

        """
        return self._args[1]

    @property
    def args(self):
        return self._args[1:]

    @property
    def func(self):
        return self._args[0]

    def __eq__(self, other):
        if type(other) is AppliedPredicate:
            return self._args == other._args
        return False

    def __hash__(self):
        return super(AppliedPredicate, self).__hash__()

    def _eval_ask(self, assumptions):
        return self.func.eval(self.arg, assumptions)

class Predicate(Boolean):
    """A predicate is a function that returns a boolean value.

    Predicates merely wrap their argument and remain unevaluated:

        >>> from sympy import Q, ask, Symbol, S
        >>> x = Symbol('x')
        >>> Q.prime(7)
        Q.prime(7)

    To obtain the truth value of an expression containing predicates, use
    the function `ask`:

        >>> ask(Q.prime(7))
        True

    The tautological predicate `Q.is_true` can be used to wrap other objects:

        >>> Q.is_true(x > 1)
        Q.is_true(x > 1)
        >>> Q.is_true(S(1) < x)
        Q.is_true(1 < x)

    """

    is_Atom = True

    def __new__(cls, name, handler=None):
        obj = Boolean.__new__(cls)
        obj.name = name
        obj.handler = handler
        return obj

    def _hashable_content(self):
        return (self.name,)

    def __getnewargs__(self):
        return (self.name,)

    def __call__(self, expr):
        return AppliedPredicate(self, expr)

    def add_handler(self, handler):
        if self.handler is None:
            self.handler = handler
        else:
            raise ValueError("Handler is already set")

    def eval(self, expr, assumptions=True):
        """
        Evaluate self(expr) under the given assumptions.

        This uses only direct resolution methods, not logical inference.
        """
        mro = inspect.getmro(type(expr))
        if self.handler is None:
            return None
        cls = get_class(self.handler)
        for subclass in mro:
            try:
                eval = getattr(cls, subclass.__name__)
            except AttributeError:
                continue
            else:
                return eval(expr, assumptions)
        else:
            return None
