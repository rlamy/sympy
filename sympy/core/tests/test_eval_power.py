from sympy.core import Rational, Symbol, Basic, S, Real, Integer
from sympy.functions.elementary.miscellaneous import sqrt
from sympy import global_assumptions, Q, Assume

def test_rational():
    a = Rational(1, 5)

    assert a**Rational(1, 2) == a**Rational(1, 2)
    assert 2 * a**Rational(1, 2) == 2 * a**Rational(1, 2)

    assert a**Rational(3, 2) == a * a**Rational(1, 2)
    assert 2 * a**Rational(3, 2) == 2*a * a**Rational(1, 2)

    assert a**Rational(17, 3) == a**5 * a**Rational(2, 3)
    assert 2 * a**Rational(17, 3) == 2*a**5 * a**Rational(2, 3)

def test_large_rational():
    e = (Rational(123712**12-1,7)+Rational(1,7))**Rational(1,3)
    assert e == 234232585392159195136 * (Rational(1,7)**Rational(1,3))

def test_negative_real():
    def feq(a,b):
        return abs(a - b) < 1E-10

    assert feq(S.One / Real(-0.5), -Integer(2))

def test_expand():
    x = Symbol('x')
    assert (2**(-1-x)).expand() == Rational(1,2)*2**(-x)

def test_issue153():
    #test that is runs:
    a = sqrt(2*(1+sqrt(2)))

def test_issue350():
    #test if powers are simplified correctly
    #see also issue 896
    a = Symbol('a')
    assert ((a**Rational(1,3))**Rational(2)) == a**Rational(2,3)
    assert ((a**Rational(3))**Rational(2,5)) == (a**Rational(3))**Rational(2,5)

    c = Symbol('c')
    d = Symbol('d')

    global_assumptions.add(Assume(c, Q.real, True))
    global_assumptions.add(Assume(d, Q.real, True))

    assert (c**2)**d == abs(c)**(2*d)
    assert sqrt(1/c) != 1/sqrt(c)
    assert (c**3)**Rational(1,3) != c

    global_assumptions.discard(Assume(c, Q.real, True))
    global_assumptions.discard(Assume(d, Q.real, True))

    z = Symbol('z')
    k = Symbol('k')
    m = Symbol('m')

    global_assumptions.add(Assume(k, Q.integer, True))
    global_assumptions.add(Assume(m, Q.integer, True))

    assert (z**k)**m == z**(k*m)
    #assert Number(5)**Rational(2,3)==Number(25)**Rational(1,3)

    global_assumptions.discard(Assume(k, Q.integer, True))
    global_assumptions.discard(Assume(m, Q.integer, True))

    c = Symbol('c')

    global_assumptions.add(Assume(c, Q.positive, True))

    assert (c**3)**Rational(2,5) == c**Rational(6,5)

    global_assumptions.discard(Assume(c, Q.positive, True))

def test_issue767():
    assert --sqrt(sqrt(5)-1)==sqrt(sqrt(5)-1)

def test_negative_one():
    x = Symbol('x', complex=True)
    y = Symbol('y', complex=True)
    assert 1/x**y == x**(-y)

def test_issue1263():
    neg = Symbol('neg')
    nonneg = Symbol('nonneg')

    global_assumptions.add(Assume(neg, Q.negative, True))
    global_assumptions.add(Assume(nonneg, Q.negative, False))

    any = Symbol('any')
    num, den = sqrt(1/neg).as_numer_denom()
    assert num == sqrt(-1)
    assert den == sqrt(-neg)
    num, den = sqrt(1/nonneg).as_numer_denom()
    assert num == 1
    assert den == sqrt(nonneg)
    num, den = sqrt(1/any).as_numer_denom()
    assert num == sqrt(1/any)
    assert den == 1

    def eqn(num, den, pow):
        return (num/den)**pow
    npos=1
    nneg=-1
    dpos=2-sqrt(3)
    dneg=1-sqrt(3)
    I = S.ImaginaryUnit
    assert dpos > 0 and dneg < 0 and npos > 0 and nneg < 0
    # pos or neg integer
    eq=eqn(npos, dpos, 2);assert eq.is_Pow and eq.as_numer_denom() == (1, dpos**2)
    eq=eqn(npos, dneg, 2);assert eq.is_Pow and eq.as_numer_denom() == (1, dneg**2)
    eq=eqn(nneg, dpos, 2);assert eq.is_Pow and eq.as_numer_denom() == (1, dpos**2)
    eq=eqn(nneg, dneg, 2);assert eq.is_Pow and eq.as_numer_denom() == (1, dneg**2)
    eq=eqn(npos, dpos, -2);assert eq.is_Pow and eq.as_numer_denom() == (dpos**2, 1)
    eq=eqn(npos, dneg, -2);assert eq.is_Pow and eq.as_numer_denom() == (dneg**2, 1)
    eq=eqn(nneg, dpos, -2);assert eq.is_Pow and eq.as_numer_denom() == (dpos**2, 1)
    eq=eqn(nneg, dneg, -2);assert eq.is_Pow and eq.as_numer_denom() == (dneg**2, 1)
    # pos or neg rational
    pow = S.Half
    eq=eqn(npos, dpos, pow);assert eq.is_Pow and eq.as_numer_denom() == (npos**pow, dpos**pow)
    eq=eqn(npos, dneg, pow);assert eq.is_Pow and eq.as_numer_denom() == ((-npos)**pow, (-dneg)**pow)
    eq=eqn(nneg, dpos, pow);assert not eq.is_Pow or eq.as_numer_denom() == (nneg**pow, dpos**pow)
    eq=eqn(nneg, dneg, pow);assert eq.is_Pow and eq.as_numer_denom() == ((-nneg)**pow, (-dneg)**pow)
    eq=eqn(npos, dpos, -pow);assert eq.is_Pow and eq.as_numer_denom() == (dpos**pow, npos**pow)
    eq=eqn(npos, dneg, -pow);assert eq.is_Pow and eq.as_numer_denom() == ((-dneg)**pow, (-npos)**pow)
    eq=eqn(nneg, dpos, -pow);assert not eq.is_Pow or eq.as_numer_denom() == (dpos**pow, nneg**pow)
    eq=eqn(nneg, dneg, -pow);assert eq.is_Pow and eq.as_numer_denom() == ((-dneg)**pow, (-nneg)**pow)
    # unknown exponent
    eq=eqn(npos, dpos, 2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(npos, dneg, 2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(nneg, dpos, 2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(nneg, dneg, 2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(npos, dpos, -2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(npos, dneg, -2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(nneg, dpos, -2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)
    eq=eqn(nneg, dneg, -2*any);assert eq.is_Pow and eq.as_numer_denom() == (eq, 1)

    global_assumptions.discard(Assume(neg, Q.negative, True))
    global_assumptions.discard(Assume(nonneg, Q.negative, False))

def test_issue1496():
    x = Symbol('x')
    y = Symbol('y')
    n = Symbol('n')

    global_assumptions.add(Assume(n, Q.even, True))
    global_assumptions.add(Assume(n, Q.integer, True))

    assert (3-y)**2 == (y-3)**2
    assert (3-y)**n == (y-3)**n
    assert (-3+y-x)**2 == (3-y+x)**2
    assert (y-3)**3 == -(3-y)**3

    global_assumptions.discard(Assume(n, Q.even, True))
    global_assumptions.discard(Assume(n, Q.integer, True))

def test_power_with_noncommutative_mul_as_base():
    x = Symbol('x', commutative=False)
    y = Symbol('y', commutative=False)
    assert not (x*y)**3 == x**3*y**3
    assert (2*x*y)**3 == 8*(x*y)**3

