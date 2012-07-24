"""
Module implementing binary operations with double dispatch.
"""

class ConflictingDefinitions(TypeError):
    pass

class binary_operation(object):
    def __init__(self, default=None):
        self.default = default
        self.dispatcher = {}

    def __call__(self, x, y):
        return self[type(x), type(y)](x, y)

    def __setitem__(self, item, func):
        self.dispatcher[item] = func

    def __getitem__(self, types):
        x_type, y_type = types
        candidates = set()
        for left in x_type.mro():
            for right in y_type.mro():
                if (left, right) not in self.dispatcher:
                    continue
                for c_left, c_right in candidates:
                    if issubclass(c_left, left) and issubclass(c_right, right):
                        break
                else:
                    for c_left, c_right in list(candidates):
                        if issubclass(left, c_left) and issubclass(right, c_right):
                            candidates.remove((c_left, c_right))
                    candidates.add((left, right))
        funcs = set(self.dispatcher[c] for c in candidates)
        if len(funcs) == 1:
            return funcs.pop()
        elif not candidates:
            return self.default
        else:
            raise ConflictingDefinitions(candidates)
