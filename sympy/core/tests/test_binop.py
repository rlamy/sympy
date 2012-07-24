from sympy.utilities.pytest import raises

from sympy.core.binop import binary_operation, ConflictingDefinitions

def test_binop():
    mul = binary_operation()
    class Monoid(object): pass
    class Ring(Monoid): pass
    class Field(Ring): pass
    mul[Ring, Ring] = lambda x, y: Ring()
    mul[Field, Field] = lambda x, y: Field()

    assert isinstance(mul(Ring(), Ring()), Ring)
    assert isinstance(mul(Field(), Field()), Field)
    assert isinstance(mul(Field(), Ring()), Ring)
    assert isinstance(mul(Ring(), Field()), Ring)
    with raises(TypeError):
        mul(Monoid(), Field())

def test_conflict():
    op = binary_operation()
    class Parent(object): pass
    class Child(Parent): pass
    op[Parent, Child] = lambda x,y: 1
    op[Child, Parent] = lambda x,y: 2

    assert op(Parent(), Child()) == 1
    assert op(Child(), Parent()) == 2
    with raises(ConflictingDefinitions):
        op(Child(), Child())

def test_no_conflict():
    op = binary_operation()
    class Parent(object): pass
    class Child(Parent): pass
    op[Parent, Child] = lambda x,y: 1
    op[Child, Parent] = op[Parent, Child]

    assert op(Parent(), Child()) == 1
    assert op(Child(), Parent()) == 1
    assert op(Child(), Child()) == 1

def test_multiple_inheritance():
    mul = binary_operation(lambda x, y: NotImplemented)
    class Scalar(object): pass
    class Vector(object): pass
    class Complex(object): pass
    class Real(Complex): pass
    class ComplexScalar(Complex, Scalar): pass
    class RealScalar(Real, ComplexScalar): pass
    class ComplexVector(Complex, Vector): pass
    class RealVector(Real, ComplexVector): pass
    mul[Scalar, Scalar] = lambda x, y: "simple_mul"
    mul[Scalar, Vector] = lambda x, y: "scalar_mul"
    mul[RealScalar, Vector] = lambda x, y: "real_mul_1"
    mul[Scalar, RealVector] = lambda x, y: "real_mul_2"

    assert mul(RealScalar(), ComplexScalar()) == "simple_mul"
    assert mul(RealVector(), ComplexVector()) == NotImplemented
    assert mul(Vector(), Scalar()) == NotImplemented
    assert mul(ComplexScalar(), ComplexVector()) == "scalar_mul"
    assert mul(RealScalar(), ComplexVector()) == "real_mul_1"
    assert mul(ComplexScalar(), RealVector()) == "real_mul_2"
    with raises(ConflictingDefinitions):
        mul(RealScalar(), RealVector())
