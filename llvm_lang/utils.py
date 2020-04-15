class _identity:
    def __get__(self, obj, owner=None):
        return self

    def __call__(self, arg):
        return arg


identity = _identity()
