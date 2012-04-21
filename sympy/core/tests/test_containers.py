from sympy import Matrix, Tuple, symbols, sympify, Basic, Integer, S
from sympy.core.containers import Tuple, tuple_wrapper, LatticeOp
from sympy.core.sympify import SympifyError

from sympy.utilities.pytest import raises
from sympy.core.compatibility import is_sequence, iterable


def test_Tuple():
    t = (1, 2, 3, 4)
    st =  Tuple(*t)
    assert set(sympify(t)) == set(st)
    assert len(t) == len(st)
    assert set(sympify(t[:2])) == set(st[:2])
    assert isinstance(st[:], Tuple)
    assert st == Tuple(1, 2, 3, 4)
    assert st.func(*st.args) == st
    p, q, r, s = symbols('p q r s')
    t2 = (p, q, r, s)
    st2 = Tuple(*t2)
    assert st2.atoms() == set(t2)
    assert st == st2.subs({p:1, q:2, r:3, s:4})
    # issue 2406
    assert all(isinstance(arg, Basic) for arg in st.args)
    assert Tuple(p, 1).subs(p, 0) == Tuple(0, 1)
    assert Tuple(p, Tuple(p, 1)).subs(p, 0) == Tuple(0, Tuple(0, 1))

    assert Tuple(t2) == Tuple(Tuple(*t2))
    assert Tuple.fromiter(t2) == Tuple(*t2)
    assert Tuple.fromiter(x for x in xrange(4)) == Tuple(0, 1, 2, 3)
    assert st2.fromiter(st2.args) == st2

def test_Tuple_contains():
    t1, t2 = Tuple(1), Tuple(2)
    assert t1 in Tuple(1, 2, 3, t1, Tuple(t2))
    assert t2 not in Tuple(1, 2, 3, t1, Tuple(t2))

def test_Tuple_concatenation():
    assert Tuple(1, 2) + Tuple(3, 4) == Tuple(1, 2, 3, 4)
    assert (1, 2) + Tuple(3, 4) == Tuple(1, 2, 3, 4)
    assert Tuple(1, 2) + (3, 4) == Tuple(1, 2, 3, 4)
    raises(TypeError, 'Tuple(1, 2) + 3')
    raises(TypeError, '1 + Tuple(2, 3)')

    #the Tuple case in __radd__ is only reached when a subclass is involved
    class Tuple2(Tuple):
        def __radd__(self, other):
            return Tuple.__radd__(self, other + other)
    assert Tuple(1, 2) + Tuple2(3, 4) == Tuple(1, 2, 1, 2, 3, 4)
    assert Tuple2(1, 2) + Tuple(3, 4) == Tuple(1, 2, 3, 4)

def test_Tuple_equality():
    assert Tuple(1, 2) is not (1, 2)
    assert (Tuple(1, 2) == (1, 2)) is True
    assert (Tuple(1, 2) != (1, 2)) is False
    assert (Tuple(1, 2) == (1, 3)) is False
    assert (Tuple(1, 2) != (1, 3)) is True
    assert (Tuple(1, 2) == Tuple(1, 2)) is True
    assert (Tuple(1, 2) != Tuple(1, 2)) is False
    assert (Tuple(1, 2) == Tuple(1, 3)) is False
    assert (Tuple(1, 2) != Tuple(1, 3)) is True

def test_Tuple_comparision():
    assert (Tuple(1, 3) >= Tuple(-10, 30)) is True
    assert (Tuple(1, 3) <= Tuple(-10, 30)) is False
    assert (Tuple(1, 3) >= Tuple(1, 3)) is True
    assert (Tuple(1, 3) <= Tuple(1, 3)) is True

def test_tuple_wrapper():

    @tuple_wrapper
    def wrap_tuples_and_return(*t):
        return t

    p = symbols('p')
    assert wrap_tuples_and_return(p, 1) == (p, 1)
    assert wrap_tuples_and_return((p, 1)) == (Tuple(p, 1),)
    assert wrap_tuples_and_return(1, (p, 2), 3) == (1, Tuple(p, 2), 3)

def test_iterable_is_sequence():
    ordered = [list(), tuple(), Tuple(), Matrix([[]])]
    unordered = [set()]
    not_sympy_iterable = [{}, '', u'']
    assert all(is_sequence(i) for i in ordered)
    assert all(not is_sequence(i) for i in unordered)
    assert all(iterable(i) for i in ordered + unordered)
    assert all(not iterable(i) for i in not_sympy_iterable)
    assert all(iterable(i, exclude=None) for i in not_sympy_iterable)

def test_Dict():
    x,y,z = symbols('x y z')
    d = Dict({x:1, y:2, z:3})
    assert d[x] == 1
    assert d[y] == 2
    raises(KeyError, 'd[2]')
    assert len(d) == 3
    assert set(d.keys()) == set((x,y,z))
    assert set(d.values()) == set((S(1),S(2),S(3)))
    assert d.get(5,'default') == 'default'
    assert x in d and z in d and not 5 in d
    assert d.has(x) and d.has(1) # SymPy Basic .has method

    # Test input types
    # input - a python dict
    # input - items as args - SymPy style
    assert (Dict({x:1, y:2, z:3}) ==
            Dict((x,1), (y,2), (z,3)))

    raises(TypeError, "Dict(((x,1), (y,2), (z,3)))")
    raises(NotImplementedError, "d[5] = 6") # assert immutability

    assert set(d.items()) == set((Tuple(x,S(1)), Tuple(y,S(2)), Tuple(z,S(3))))
    assert set(d) == set([x,y,z])
    assert str(d) == '{x: 1, y: 2, z: 3}'
    assert d.__repr__() == '{x: 1, y: 2, z: 3}'

def issue_2689():
    args = [(1,2),(2,1)]
    for o in [Dict, Tuple, FiniteSet]:
        # __eq__ and arg handling
        if o != Tuple:
            assert o(*args) == o(*reversed(args))
        pair = [o(*args), o(*reversed(args))]
        assert sorted(pair) == sorted(reversed(pair))
        assert set(o(*args)) # doesn't fail

# create the simplest possible Lattice class
class join(LatticeOp):
    zero = Integer(0)
    identity = Integer(1)

def test_lattice_simple():
    assert join(join(2, 3), 4) == join(2, join(3, 4))
    assert join(2, 3) == join(3, 2)
    assert join(0, 2) == 0
    assert join(1, 2) == 2
    assert join(2, 2) == 2

    assert join(join(2, 3), 4) == join(2, 3, 4)
    assert join() == 1
    assert join(4) == 4
    assert join(1, 4, 2, 3, 1, 3, 2) == join(2, 3, 4)

def test_lattice_shortcircuit():
    raises(SympifyError, 'join(object)')
    assert join(0, object) == 0

def test_lattice_print():
    assert str(join(5, 4, 3, 2)) == 'join(2, 3, 4, 5)'

def test_lattice_make_args():
    assert join.make_args(0) == set([0])
    assert join.make_args(1) == set([1])
    assert join.make_args(join(2, 3, 4)) == set([S(2), S(3), S(4)])

