
from sympy.core.function import FuncExpr, builtin
from sympy.core import sympify, S
from sympy.utilities.decorator import deprecated

###############################################################################
###################### Kronecker Delta, Levi-Civita etc. ######################
###############################################################################

#@builtin
class _Dij(FuncExpr):
    """
    Represents the Kronecker Delta Function

    if i == j, Dij(i, j) = 1
    otherwise Dij(i, j) = 0
    where i, j are usually integers
    """
    nargs = (1, 2)

    @classmethod
    @deprecated
    def canonize(cls, i, j=0):
        return cls.eval(i, j)

    @classmethod
    def eval(cls, i, j=0):
        i, j = map(sympify, (i, j))
        if i == j:
            return S.One
        elif i.is_number and j.is_number:
            return S.Zero
Dij = builtin(_Dij)


#@builtin
class _Eijk(FuncExpr):
    """
    Represents the Levi-Civita symbol (antisymmetric symbol)
    """
    nargs = 3

    @classmethod
    @deprecated
    def canonize(cls, i, j, k):
        return cls.eval(i, j, k)

    @classmethod
    def eval(cls, i, j, k):
        i, j, k = map(sympify, (i, j, k))
        if (i,j,k) in [(1,2,3), (2,3,1), (3,1,2)]:
            return S.One
        elif (i,j,k) in [(1,3,2), (3,2,1), (2,1,3)]:
            return S.NegativeOne
        elif i==j or j==k or k==i:
            return S.Zero
Eijk = builtin(_Eijk)
