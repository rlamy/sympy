""" Strategies to Traverse a Tree """
from util import is_leaf

def top_down(rule):
    """ Apply a rule down a tree running it on the top nodes first """
    def top_down_rl(expr):
        newexpr = rule(expr)
        if is_leaf(newexpr):
            return newexpr
        return type(newexpr)(*map(top_down_rl, newexpr.args))
    return top_down_rl

def bottom_up(rule):
    """ Apply a rule down a tree running it on the bottom nodes first """
    def bottom_up_rl(expr):
        if is_leaf(expr):
            return rule(expr)
        else:
            return rule(type(expr)(*map(bottom_up_rl, expr.args)))
    return bottom_up_rl
