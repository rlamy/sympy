from sympy.core import Basic, Symbol
from sympy.core.evalf import as_mpmath
from sympy.mpmath.settings import dps_to_prec
import sympy.mpmath as mpmath
import math

def _determine_prec(**kwargs):
    # Determine precision. (This follows evalf.Basic_evalf)
    if 'prec' in kwargs:
        prec = int(kwargs['prec'] * math.log(10, 2))
    else:
        prec = dps_to_prec(15)
    return prec

def _generate_lambda(expr, sym, prec):
    return lambda x: as_mpmath(expr.subs(sym, x), prec, {})

def plot(f, *args, **kwargs):
    """
    Shows a simple 2D plot of a function `f(x)` or list of functions
    `[f_0(x), f_1(x), \ldots, f_n(x)]` over a given interval
    specified by *xlim*. For example:

    >>> from sympy import plot, exp
    >>> x = Symbol('x')
    >>> plot(exp(x), x, [1, 4])

    This function also accepts the same arguments that mpmath.plot does.
    Please see the mpmath documention for details.

    NOTE: This function requires matplotlib (pylab).
    """
    # Listify 'f' if necessary.
    if not isinstance(f, list):
        if len(args) > 0 and isinstance(args[0], Symbol):
            f = [(f, args[0])]
            args = args[1:]
        else:
            f = [f]

    # Determine precision.
    prec = _determine_prec(**kwargs)

    # Compose an argument suitable for the mpmath plot functions.
    f_mpmath = []
    for func in f:
        # Listify 'func' if necessary.
        if not isinstance(func, tuple):
            func = [func]

        if isinstance(func[0], Basic):
            # We are plotting a sympy expression.
            expr = func[0]
            if len(func) > 1 and isinstance(func[1], Symbol):
                # Symbol explictly specified.
                sym = func[1]
            else:
                # No Symbol specified: Guess which Symbol to use.
                # (Currently a randomly selected contained Symbol)
                syms = expr.atoms(Symbol)
                if len(syms) > 0:
                    sym = list(syms)[0]

            f_mpmath.append(_generate_lambda(expr, sym, prec))
        else:
            f_mpmath.append(func[0])

    # Let mpmath take care of the actual plotting.
    mpmath.plot(f_mpmath, *args, **kwargs)

def cplot(f, *args, **kwargs):
    """
    Plots the given complex-valued function *f* over a rectangular part
    of the complex plane specified by the pairs of intervals *re* and *im*.
    For example::

    >>> from sympy import cplot
    >>> z = Symbol('z')
    >>> cplot(z, z, [-5, 5], [-5, 5])

    This function also accepts the same arguments that mpmath.cplot does.
    Please see the mpmath documention for details.

    NOTE: This function requires matplotlib (pylab).
    """
    # Determine precision. (This follows evalf.Basic_evalf)
    prec = _determine_prec(**kwargs)

    # Compose an argument suitable for the mpmath plot functions.
    if isinstance(f, Basic):
        # We are plotting a sympy expression.
        if len(args) > 0 and isinstance(args[0], Symbol):
            # Symbol explictly specified.
            sym = args[0]
            args = args[1:]
        else:
            # No Symbol specified: Guess which Symbol to use.
            # (Currently a randomly selected contained Symbol)
            syms = f.atoms(Symbol)
            if len(syms) > 0:
                sym = list(syms)[0]

        f_mpmath = _generate_lambda(f, sym, prec)
    else:
        f_mpmath = f

    # Let mpmath take care of the actual plotting.
    mpmath.cplot(f_mpmath, *args, **kwargs)
