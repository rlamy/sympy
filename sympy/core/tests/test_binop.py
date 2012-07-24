from sympy.utilities.pytest import raises

from sympy.core.binop import binary_operation

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
