from core import C
from basic import Basic
from singleton import S
from expr import Expr
from sympify import _sympify, sympify
from cache import cacheit
from compatibility import cmp


class AssocOp(Expr):
    """ Associative operations, can separate noncommutative and
    commutative parts.

    (a op b) op c == a op (b op c) == a op b op c.

    Base class for Add and Mul.

    This is an abstract base class, concrete derived classes must define
    the attribute `identity`.
    """

    # for performance reason, we don't let is_commutative go to assumptions,
    # and keep it right here
    __slots__ = ['is_commutative']

    @cacheit
    def __new__(cls, *args, **options):
        args = map(_sympify, args)
        args = [a for a in args if a is not cls.identity]

        if not options.pop('evaluate', True):
            return cls._from_args(args)

        if len(args) == 0:
            return cls.identity
        if len(args) == 1:
            return args[0]

        c_part, nc_part, order_symbols = cls.flatten(args)
        obj = cls._from_args(c_part + nc_part, not nc_part)

        if order_symbols is not None:
            return C.Order(obj, *order_symbols)
        return obj

    @classmethod
    def _from_args(cls, args, is_commutative=None):
        """Create new instance with already-processed args"""
        if len(args) == 0:
            return cls.identity
        elif len(args) == 1:
            return args[0]

        obj = Expr.__new__(cls, *args)
        if is_commutative is None:
            is_commutative = all(a.is_commutative for a in args)
        obj.is_commutative = is_commutative
        return obj

    def _new_rawargs(self, *args, **kwargs):
        """Create new instance of own class with args exactly as provided by
        caller but returning the self class identity if args is empty.

           This is handy when we want to optimize things, e.g.

               >>> from sympy import Mul, symbols, S
               >>> from sympy.abc import x, y
               >>> e = Mul(3, x, y)
               >>> e.args
               (3, x, y)
               >>> Mul(*e.args[1:])
               x*y
               >>> e._new_rawargs(*e.args[1:])  # the same as above, but faster
               x*y

           Note: use this with caution. There is no checking of arguments at
           all. This is best used when you are rebuilding an Add or Mul after
           simply removing one or more terms. If modification which result,
           for example, in extra 1s being inserted (as when collecting an
           expression's numerators and denominators) they will not show up in
           the result but a Mul will be returned nonetheless:

               >>> m = (x*y)._new_rawargs(S.One, x); m
               x
               >>> m == x
               False
               >>> m.is_Mul
               True

           Another issue to be aware of is that the commutativity of the result
           is based on the commutativity of self. If you are rebuilding the
           terms that came from a commutative object then there will be no
           problem, but if self was non-commutative then what you are
           rebuilding may now be commutative.

           Although this routine tries to do as little as possible with the
           input, getting the commutativity right is important, so this level
           of safety is enforced: commutativity will always be recomputed if
           self is non-commutative and kwarg `reeval=False` has not been
           passed.
        """
        if kwargs.pop('reeval', True) and self.is_commutative is False:
            is_commutative = None
        else:
            is_commutative = self.is_commutative
        return self._from_args(args, is_commutative)

    @classmethod
    def flatten(cls, seq):
        """Return seq so that none of the elements are of type `cls`. This is
        the vanilla routine that will be used if a class derived from AssocOp
        does not define its own flatten routine."""
        # apply associativity, no commutativity property is used
        new_seq = []
        while seq:
            o = seq.pop()
            if o.__class__ is cls: # classes must match exactly
                seq.extend(o.args)
            else:
                new_seq.append(o)
        # c_part, nc_part, order_symbols
        return [], new_seq, None

    def _matches_commutative(self, expr, repl_dict={}):
        """
        Matches Add/Mul "pattern" to an expression "expr".

        repl_dict ... a dictionary of (wild: expression) pairs, that get
                      returned with the results

        This function is the main workhorse for Add/Mul.

        For instance:

        >>> from sympy import symbols, Wild, sin
        >>> a = Wild("a")
        >>> b = Wild("b")
        >>> c = Wild("c")
        >>> x, y, z = symbols("x y z")
        >>> (a+sin(b)*c)._matches_commutative(x+sin(y)*z)
        {a_: x, b_: y, c_: z}

        In the example above, "a+sin(b)*c" is the pattern, and "x+sin(y)*z" is
        the expression.

        The repl_dict contains parts that were already matched. For example
        here:

        >>> (x+sin(b)*c)._matches_commutative(x+sin(y)*z, repl_dict={a: x})
        {a_: x, b_: y, c_: z}

        the only function of the repl_dict is to return it in the
        result, e.g. if you omit it:

        >>> (x+sin(b)*c)._matches_commutative(x+sin(y)*z)
        {b_: y, c_: z}

        the "a: x" is not returned in the result, but otherwise it is
        equivalent.

        """
        # handle simple patterns
        if self == expr:
            return repl_dict

        d = self._matches_simple(expr, repl_dict)
        if d is not None:
            return d

        # eliminate exact part from pattern: (2+a+w1+w2).matches(expr) -> (w1+w2).matches(expr-a-2)
        wild_part = []
        exact_part = []
        from function import WildFunction
        from symbol import Wild
        for p in self.args:
            if p.has(Wild, WildFunction) and (not expr.has(p)):
                # not all Wild should stay Wilds, for example:
                # (w2+w3).matches(w1) -> (w1+w3).matches(w1) -> w3.matches(0)
                wild_part.append(p)
            else:
                exact_part.append(p)

        if exact_part:
            newpattern = self.func(*wild_part)
            newexpr = self._combine_inverse(expr, self.func(*exact_part))
            return newpattern.matches(newexpr, repl_dict)

        # now to real work ;)
        if expr.is_Add:
            i, d = expr.as_independent(C.Symbol)
            expr_list = (i,) + self.make_args(expr)
        else:
            expr_list = self.make_args(expr)
        for last_op in reversed(expr_list):
            for w in reversed(wild_part):
                d1 = w.matches(last_op, repl_dict)
                if d1 is not None:
                    d2 = self.xreplace(d1).matches(expr, d1)
                    if d2 is not None:
                        return d2

        return

    def _eval_template_is_attr(self, is_attr, when_multiple=False):
        # return True if all elements have the property;
        # False if one doesn't have the property; and
        # if more than one doesn't have property, return
        #    False if when_multiple = False
        #    None if when_multiple is not False
        quick = when_multiple is None
        multi = False
        for t in self.args:
            a = getattr(t, is_attr)
            if a is True:
                continue
            if a is None:
                return
            if quick and multi:
                return None
            multi = True
        return not multi

    def _eval_evalf(self, prec):
        return self.func(*[s._evalf(prec) for s in self.args])

    @classmethod
    def make_args(cls, expr):
        """
        Return a sequence of elements `args` such that cls(*args) == expr

        >>> from sympy import Symbol, Mul, Add
        >>> x, y = map(Symbol, 'xy')

        >>> Mul.make_args(x*y)
        (x, y)
        >>> Add.make_args(x*y)
        (x*y,)
        >>> set(Add.make_args(x*y + y)) == set([y, x*y])
        True

        """
        if isinstance(expr, cls):
            return expr.args
        else:
            return (expr,)
