"""
Module implementing binary operations with double dispatch.
"""

class binary_operation(object):
    def __init__(self):
        self.default = None
        self.dispatcher = {}

    def __call__(self, x, y):
        return self[type(x), type(y)](x, y)

    def __setitem__(self, item, func):
        self.dispatcher[item] = func

    def __getitem__(self, types):
        x_type, y_type = types
        for left in x_type.mro():
            for right in y_type.mro():
                try:
                    return self.dispatcher[left, right]
                except KeyError:
                    pass
