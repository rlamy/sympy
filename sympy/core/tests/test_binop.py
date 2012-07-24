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
