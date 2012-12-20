from sympy.core import Add, Basic, symbols, Mul, Wild, FiniteSet
from sympy.logic import And
from sympy.unify.core import Compound, Variable
from sympy.unify.usympy import (deconstruct, construct, unify, is_associative,
        is_commutative)
from sympy.abc import w, x, y, z, n, m, k
from sympy.utilities.pytest import XFAIL

def test_deconstruct():
    expr = Basic(1, 2, 3)
    expected = Compound(Basic, (1, 2, 3))
    assert deconstruct(expr) == expected
    a = Wild('a', properties=[lambda x: x.is_positive])
    assert deconstruct(a) == deconstruct(a)

def test_construct():
    expr     = Compound(Basic, (1, 2, 3))
    expected = Basic(1, 2, 3)
    assert construct(expr) == expected

def test_nested():
    expr = Basic(1, Basic(2), 3)
    cmpd = Compound(Basic, (1, Compound(Basic, (2,)), 3))
    assert deconstruct(expr) == cmpd
    assert construct(cmpd) == expr

def test_unify():
    expr = Basic(1, 2, 3)
    a, b, c = map(Wild, 'abc')
    pattern = Basic(a, b, c)
    assert list(unify(expr, pattern, {})) == [{a: 1, b: 2, c: 3}]
    assert list(unify(expr, pattern))     == [{a: 1, b: 2, c: 3}]

def test_s_input():
    expr = Basic(1, 2)
    a, b = map(Wild, 'ab')
    pattern = Basic(a, b)
    assert list(unify(expr, pattern, {})) == [{a: 1, b: 2}]
    assert list(unify(expr, pattern, {a: 5})) == []

def iterdicteq(a, b):
    a = tuple(a)
    b = tuple(b)
    return len(a) == len(b) and all(x in b for x in a)

def test_unify_commutative():
    expr = Add(1, 2, 3, evaluate=False)
    a, b, c = map(Wild, 'abc')
    pattern = Add(a, b, c, evaluate=False)

    result  = tuple(unify(expr, pattern, {}))
    expected = ({a: 1, b: 2, c: 3},
                {a: 1, b: 3, c: 2},
                {a: 2, b: 1, c: 3},
                {a: 2, b: 3, c: 1},
                {a: 3, b: 1, c: 2},
                {a: 3, b: 2, c: 1})

    assert iterdicteq(result, expected)

def test_unify_iter():
    expr = Add(1, 2, 3, evaluate=False)
    a, b, c = map(Wild, 'abc')
    pattern = Add(a, c, evaluate=False)
    assert is_associative(deconstruct(pattern))
    assert is_commutative(deconstruct(pattern))

    result   = list(unify(expr, pattern, {}))
    expected = [{a: 1, c: Add(2, 3, evaluate=False)},
                {a: 1, c: Add(3, 2, evaluate=False)},
                {a: 2, c: Add(1, 3, evaluate=False)},
                {a: 2, c: Add(3, 1, evaluate=False)},
                {a: 3, c: Add(1, 2, evaluate=False)},
                {a: 3, c: Add(2, 1, evaluate=False)},
                {a: Add(1, 2, evaluate=False), c: 3},
                {a: Add(2, 1, evaluate=False), c: 3},
                {a: Add(1, 3, evaluate=False), c: 2},
                {a: Add(3, 1, evaluate=False), c: 2},
                {a: Add(2, 3, evaluate=False), c: 1},
                {a: Add(3, 2, evaluate=False), c: 1}]

    assert iterdicteq(result, expected)

def test_hard_match():
    from sympy import sin, cos
    expr = sin(x) + cos(x)**2
    p, q = map(Wild, 'pq')
    pattern = sin(p) + cos(p)**2
    assert list(unify(expr, pattern, {})) == [{p: x}]


def test_matrix():
    from sympy import MatrixSymbol
    Y = MatrixSymbol('Y', 2, 2)
    Z = MatrixSymbol('Z', 2, 3)
    n = Wild('n')
    p = MatrixSymbol('X', n, n)
    assert list(unify(p, Y, {})) == [{'X': 'Y', n: 2}]
    assert list(unify(p, Z, {})) == []

def test_wilds_in_wilds():
    from sympy import MatrixSymbol, MatMul
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', m, k)
    pattern = patternify(A*B, 'A', n, m, B) # note that m is in B as well
    assert deconstruct(pattern) == Compound(MatMul, (Compound(MatrixSymbol,
        (Variable('A'), Variable(n), Variable(m))), Variable(B)))

def test_non_frankenAdds():
    # the is_commutative property used to fail because of Basic.__new__
    # This caused is_commutative and str calls to fail
    expr = x+y*2
    rebuilt = construct(deconstruct(expr))
    # Ensure that we can run these commands without causing an error
    str(rebuilt)
    rebuilt.is_commutative

def test_FiniteSet_commutivity():
    a, b, c = symbols('a, b, c')
    x, y = map(Wild, 'xy')
    s = FiniteSet(a, b, c)
    t = FiniteSet(x, y)
    assert {x: FiniteSet(a, c), y: b} in tuple(unify(s, t))

def test_FiniteSet_complex():
    c, x, y, z = symbols('c, x, y, z')
    a, b = symbols('a, b', cls=Wild)
    expr = FiniteSet(Basic(1, x), y, Basic(x, z))
    expected = tuple([{b: 1, a: FiniteSet(y, Basic(x, z))},
                      {b: z, a: FiniteSet(y, Basic(1, x))}])
    pattern = FiniteSet(a, Basic(x, b))
    assert iterdicteq(unify(expr, pattern), expected)

def test_with_types():
    a, b, c = symbols('a, b, c')
    x = Wild('x', properties=[lambda x: isinstance(x, Mul)])
    y = Wild('y')
    expr = a*b + c
    assert list(unify(expr, x+y)) == [{x: a*b, y: c}]

@XFAIL
def test_and():
    a, b = symbols('a, b', Wild)
    str(list(unify((x>0) & (z<3), And(a, b))))
