from functools import singledispatch

from . import node


def assert_all_registered(func: singledispatch):
    unregistered_types = []

    for export in node.__all__:
        nodetype = node.__dict__[export]
        if not issubclass(nodetype, node.Node):
            continue
        if nodetype not in func.registry:
            unregistered_types.append(export)

    assert not unregistered_types, (
        f'{func.__name__}: missing implementations for ' +
        ', '.join(unregistered_types))
