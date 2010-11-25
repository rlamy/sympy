from sympy import Symbol, exp, Integer, Real, sin, cos, log, Poly, Lambda, \
        Function, I, S, sqrt,  raises, srepr, Rational
from sympy.abc import x, y
from sympy.core.sympify import convert, _sympify, SympifyError
from sympy.core.decorators import _sympifyit

def test_439():
    v = convert("exp(x)")
    x = Symbol("x")
    assert v == exp(x)
    assert type(v) == type(exp(x))
    assert str(type(v)) == str(type(exp(x)))

def test_convert1():
    assert convert("x") == Symbol("x")
    assert convert("   x") == Symbol("x")
    assert convert("   x   ") == Symbol("x")
    # 1778
    n1 = Rational(1, 2)
    assert convert('--.5') == n1
    assert convert('-1/2') == -n1
    assert convert('-+--.5') == -n1
    assert convert('-.[3]') == Rational(-1, 3)
    assert convert('.[3]') == Rational(1, 3)
    assert convert('+.[3]') == Rational(1, 3)
    assert convert('+0.[3]*10**-2') == Rational(1, 300)
    # options to make reals into rationals
    assert convert('1.22[345]', rational=1) == \
           1 + Rational(22, 100) + Rational(345, 99900)
    assert convert('2/2.6', rational=1) == Rational(10, 13)
    assert convert('2.6/2', rational=1) == Rational(13, 10)
    assert convert('2.6e2/17', rational=1) == Rational(260, 17)
    assert convert('2.6e+2/17', rational=1) == Rational(260, 17)
    assert convert('2.6e-2/17', rational=1) == Rational(26, 17000)
    assert convert('2.1+3/4', rational=1) == Rational(21, 10) + Rational(3, 4)
    assert convert('2.234456', rational=1) == Rational(279307, 125000)
    assert convert('2.234456e23', rational=1) == 223445600000000000000000
    assert convert('2.234456e-23', rational=1) == Rational(279307, 12500000000000000000000000000)
    assert convert('-2.234456e-23', rational=1) == Rational(-279307, 12500000000000000000000000000)
    assert convert('12345678901/17', rational=1) == Rational(12345678901, 17)
    assert convert('1/.3 + x', rational=1) == Rational(10, 3) + x
    # make sure longs in fractions work
    assert convert('222222222222/11111111111') == Rational(222222222222, 11111111111)
    # ... even if they come from repetend notation
    assert convert('1/.2[123456789012]') == Rational(333333333333, 70781892967)
    # ... or from high precision reals
    assert convert('.1234567890123456', rational=1) == Rational(19290123283179,  156250000000000)

def test_convert2():
    class A:
        def _sympy_(self):
            return Symbol("x")**3

    a = A()

    assert _sympify(a)== x**3
    assert convert(a) == x**3
    assert a == x**3

def test_convert3():
    assert convert("x**3") == x**3
    assert convert("x^3") == x**3
    assert convert("1/2") == Integer(1)/2

    raises(SympifyError, "_sympify('x**3')")
    raises(SympifyError, "_sympify('1/2')")

def test_sympify_bool():
    """Test that sympify accepts boolean values
    and that output leaves them unchanged"""
    assert convert(True) == True
    assert convert(False)== False

def test_sympyify_iterables():
    ans = [Rational(3, 10), Rational(1, 5)]
    assert convert(['.3', '.2'], rational=1) == ans
    assert convert(set(['.3', '.2']), rational=1) == set(ans)
    assert convert(tuple(['.3', '.2']), rational=1) == tuple(ans)

def test_sympify4():
    class A:
        def _sympy_(self):
            return Symbol("x")

    a = A()

    assert _sympify(a)**3== x**3
    assert convert(a)**3 == x**3
    assert a == x

def test_convert_text():
    assert convert('some') == Symbol('some')
    assert convert('core') == Symbol('core')

    assert convert('True') == True
    assert convert('False') == False

    assert convert('Poly') == Poly
    assert convert('sin') == sin

def test_convert_function():
    assert convert('factor(x**2-1, x)') == -(1-x)*(x+1)
    assert convert('sin(pi/2)*cos(pi)') == -Integer(1)

def test_sympify_poly():
    p = Poly(x**2+x+1, x)

    assert _sympify(p) is p
    assert convert(p) is p

def test_sage():
    # how to effectivelly test for the _sage_() method without having SAGE
    # installed?
    assert hasattr(x, "_sage_")
    assert hasattr(Integer(3), "_sage_")
    assert hasattr(sin(x), "_sage_")
    assert hasattr(cos(x), "_sage_")
    assert hasattr(x**2, "_sage_")
    assert hasattr(x+y, "_sage_")
    assert hasattr(exp(x), "_sage_")
    assert hasattr(log(x), "_sage_")

def test_bug496():
    a_ = convert("a_")
    _a = convert("_a")

def test_lambda():
    x = Symbol('x')
    assert convert('lambda : 1') == Lambda(x, 1)
    assert convert('lambda x: 2*x') == Lambda(x, 2*x)
    assert convert('lambda x, y: 2*x+y') == Lambda([x, y], 2*x+y)

    raises(SympifyError, "_sympify('lambda : 1')")

def test_sympify_raises():
    raises(SympifyError, 'convert("fx)")')


def test__sympify():
    x = Symbol('x')
    f = Function('f')

    # positive _sympify
    assert _sympify(x)      is x
    assert _sympify(f)      is f
    assert _sympify(1)      == Integer(1)
    assert _sympify(0.5)    == Real("0.5")
    assert _sympify(1+1j)   == 1 + I

    class A:
        def _sympy_(self):
            return Integer(5)

    a = A()
    assert _sympify(a)      == Integer(5)

    # negative _sympify
    raises(SympifyError, "_sympify('1')")
    raises(SympifyError, "_sympify([1,2,3])")


def test_sympifyit():
    x = Symbol('x')
    y = Symbol('y')

    @_sympifyit('b', NotImplemented)
    def add(a, b):
        return a+b

    assert add(x, 1)    == x+1
    assert add(x, 0.5)  == x+Real('0.5')
    assert add(x, y)    == x+y

    assert add(x, '1')  == NotImplemented


    @_sympifyit('b')
    def add_raises(a, b):
        return a+b

    assert add_raises(x, 1)     == x+1
    assert add_raises(x, 0.5)   == x+Real('0.5')
    assert add_raises(x, y)     == x+y

    raises(SympifyError, "add_raises(x, '1')")

def test_int_float():
    class F1_1(object):
        def __float__(self):
            return 1.1

    class F1_1b(object):
        """
        This class is still a float, even though it also implements __int__().
        """
        def __float__(self):
            return 1.1

        def __int__(self):
            return 1

    class F1_1c(object):
        """
        This class is still a float, because it implements _sympy_()
        """
        def __float__(self):
            return 1.1

        def __int__(self):
            return 1

        def _sympy_(self):
            return Real(1.1)

    class I5(object):
        def __int__(self):
            return 5

    class I5b(object):
        """
        This class implements both __int__() and __float__(), so it will be
        treated as Real in SymPy. One could change this behavior, by using
        float(a) == int(a), but deciding that integer-valued floats represent
        exact numbers is arbitrary and often not correct, so we do not do it.
        If, in the future, we decide to do it anyway, the tests for I5b need to
        be changed.
        """
        def __float__(self):
            return 5.0

        def __int__(self):
            return 5

    class I5c(object):
        """
        This class implements both __int__() and __float__(), but also
        a _sympy_() method, so it will be Integer.
        """
        def __float__(self):
            return 5.0

        def __int__(self):
            return 5

        def _sympy_(self):
            return Integer(5)

    i5 = I5()
    i5b = I5b()
    i5c = I5c()
    f1_1 = F1_1()
    f1_1b = F1_1b()
    f1_1c = F1_1c()
    assert convert(i5) == 5
    assert isinstance(convert(i5), Integer)
    assert convert(i5b) == 5
    assert isinstance(convert(i5b), Real)
    assert convert(i5c) == 5
    assert isinstance(convert(i5c), Integer)
    assert abs(convert(f1_1) - 1.1) < 1e-5
    assert abs(convert(f1_1b) - 1.1) < 1e-5
    assert abs(convert(f1_1c) - 1.1) < 1e-5

    assert _sympify(i5) == 5
    assert isinstance(_sympify(i5), Integer)
    assert _sympify(i5b) == 5
    assert isinstance(_sympify(i5b), Real)
    assert _sympify(i5c) == 5
    assert isinstance(_sympify(i5c), Integer)
    assert abs(_sympify(f1_1) - 1.1) < 1e-5
    assert abs(_sympify(f1_1b) - 1.1) < 1e-5
    assert abs(_sympify(f1_1c) - 1.1) < 1e-5


def test_issue1034():
    a = convert('Integer(4)')

    assert a == Integer(4)
    assert a.is_Integer

def test_issue883():
    a = [3,2.0]
    assert convert(a) == [Integer(3), Real(2.0)]
    assert convert(tuple(a)) == (Integer(3), Real(2.0))
    assert convert(set(a)) == set([Integer(3), Real(2.0)])

def test_S_convert():
    assert S(1)/2 == convert(1)/2
    assert (-2)**(S(1)/2) == sqrt(2)*I

def test_issue1689():
    assert srepr(S(1.0+0J)) == srepr(S(1.0)) == srepr(Real(1.0))
    assert srepr(Real(1)) != srepr(Real(1.0))

def test_issue1699_None():
    assert S(None) == None

def test_issue1889_Builtins():
    C = Symbol('C')
    vars = {}
    vars['C'] = C
    exp1 = convert('C')
    assert( exp1 == C )	# Make sure it did not get mixed up with sympy.C

    exp2 = convert('C', vars)
    assert( exp2 == C ) # Make sure it did not get mixed up with sympy.C
