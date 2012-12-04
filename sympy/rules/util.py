from sympy.core import Basic

def is_leaf(x):
    return not isinstance(x, Basic) or x.is_Atom
