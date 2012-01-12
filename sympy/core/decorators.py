"""
SymPy core decorators.

The purpose of this module is to expose decorators without any other
dependencies, so that they can be easily imported anywhere in sympy/core.
"""

from functools import wraps
from sympify import SympifyError, sympify
from sympy.core.compatibility import SymPyDeprecationWarning
import warnings

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=SymPyDeprecationWarning)
        return func(*args, **kwargs)
    return new_func

def _sympifyit(arg, retval=None):
    """decorator to smartly _sympify function arguments

       @_sympifyit('other', NotImplemented)
       def add(self, other):
           ...

       In add, other can be thought of as already being a SymPy object.

       If it is not, the code is likely to catch an exception, then other will
       be explicitly _sympified, and the whole code restarted.

       if _sympify(arg) fails, NotImplemented will be returned

       see: __sympifyit
    """
    def deco(func):
        return __sympifyit(func, arg, retval)

    return deco

def __sympifyit(func, arg, retval=None):
    """decorator to _sympify `arg` argument for function `func`

       don't use directly -- use _sympifyit instead
    """

    # we support f(a,b) only
    assert func.func_code.co_argcount
    # only b is _sympified
    assert func.func_code.co_varnames[1] == arg

    if retval is None:
        @wraps(func)
        def __sympifyit_wrapper(a, b):
            return func(a, sympify(b, strict=True))

    else:
        @wraps(func)
        def __sympifyit_wrapper(a, b):
            try:
                return func(a, sympify(b, strict=True))
            except SympifyError:
                return retval

    return __sympifyit_wrapper
