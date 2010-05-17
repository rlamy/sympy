from sympy.logic.boolalg import conjuncts
from sympy.assumptions import Q, ask, refine_logic

class AskHandler(object):
    """Base class that all Ask Handlers must inherit"""
    pass

class CommonHandler(AskHandler):
    """Defines some useful methods common to most Handlers """

    @staticmethod
    def NaN(expr, assumptions):
        return False

class AskCommutativeHandler(CommonHandler):
    """
    Handler for key 'commutative'
    """

    @staticmethod
    def Symbol(expr, assumptions):
        """Objects are expected to be commutative unless otherwise stated"""
        assumps = conjuncts(assumptions)
        if Q.commutative(expr) in assumps:
            return True
        elif ~Q.commutative(expr) in assumps:
            return False
        return True

    @staticmethod
    def Basic(expr, assumptions):
        for arg in expr.args:
            if not ask(arg, Q.commutative, assumptions):
                return False
        return True

    @staticmethod
    def Number(expr, assumptions):
        return True

    @staticmethod
    def NaN(expr, assumptions):
        return True

class TautologicalHandler(AskHandler):
    """Wrapper allowing to query the truth value of a boolean expression."""

    @staticmethod
    def bool(expr, assumptions):
        return expr

    @staticmethod
    def ApplyPredicate(expr, assumptions):
        return refine_logic(expr, assumptions)

    @staticmethod
    def BooleanFunction(expr, assumptions):
        return expr.func(*[refine_logic(arg, assumptions) for arg in expr.args])
