"""Logic expressions handling

This is mainly needed for facts.py.
"""
from sympy.logic.boolalg import fuzzy_not, Boolean, And as _And, Or as _Or, Not as _Not
from sympy.core.basic import Basic, Atom

def fuzzy_bool(x):
    """Return True, False or None according to x.

    Whereas bool(x) returns True or False, fuzzy_bool allows
    for the None value.
    """
    if x is None:
        return None
    return bool(x)

def fuzzy_and(*args):
    """Return True (all True), False (any False) or None.

    If `a` is an iterable it must have more than one element."""

    if (len(args) == 1 and hasattr(args[0], '__iter__') or
        len(args) > 2):
        if len(args) == 1:
            args = args[0]
        rv = True
        i = 0
        for ai in args:
            ai = fuzzy_bool(ai)
            if ai is False:
                return False
            if rv: # this will stop updating if a None is ever trapped
                rv = ai
            i += 1
        if i < 2:
            raise ValueError('iterables must have 2 or more elements')
        return rv

    a, b = [fuzzy_bool(i) for i in args]
    if a is True and b is True:
        return True
    elif a is False or b is False:
        return False

class Fact(Atom, Boolean):
    @property
    def arg(self):
        return self._args[0]

    def __str__(self):
        return self.arg

    def __eq__(self, other):
        return other == self.arg

    def __ne__(self, other):
        return other != self.arg

    def __hash__(self):
        return hash(self.arg)


class Logic(object):
    """Logical expression"""
    pass


class And(_And, Logic):

    def __new__(cls, *args):
        obj = super(And, cls).__new__(cls, *args)
        argset = _And.make_args(obj)
        for a in argset:
            if Not(a) in argset:
                return False
        return obj

    def _eval_propagate_not(self):
        # !(a&b&c ...) == !a | !b | !c ...
        return Or( *[Not(a) for a in self.args] )


    # (a|b|...) & c == (a&c) | (b&c) | ...
    def expand(self):

        # first locate Or
        for i in range(len(self.args)):
            arg = self.args[i]
            if isinstance(arg, Or):
                arest = self.args[:i] + self.args[i+1:]

                orterms = [And( *(arest + (a,)) ) for a in arg.args]
                for j in range(len(orterms)):
                    if isinstance(orterms[j], Logic):
                        orterms[j] = orterms[j].expand()

                res = Or(*orterms)
                return res

        else:
            return self


class Or(_Or, Logic):

    def __new__(cls, *args):
        obj = super(Or, cls).__new__(cls, *args)
        argset = _Or.make_args(obj)
        for a in argset:
            if Not(a) in argset:
                return True
        return obj

    def _eval_propagate_not(self):
        # !(a|b|c ...) == !a & !b & !c ...
        return And( *[Not(a) for a in self.args] )

class Not(_Not, Logic):

    def __new__(cls, arg):
        if isinstance(arg, Logic):
            # XXX this is a hack to expand right from the beginning
            arg = arg._eval_propagate_not()
            return arg
        else:
            return _Not.__new__(cls, arg)

    def _eval_propagate_not(self):
        return self.arg

    @property
    def arg(self):
        return self.args[0]
