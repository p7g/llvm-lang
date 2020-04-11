import warnings

from abc import ABC
from functools import singledispatch
from typing import Callable, Iterable

from . import node


def expect_all_concrete_nodes(name: str,
                              fn: Callable[[str], bool],
                              *,
                              exclude: Iterable[str] = None):
    all_nodes = set(node.__all__)

    if exclude is not None:
        to_exclude = set(exclude)
        assert to_exclude.issubset(
            all_nodes), 'Exclusions must be a subset of node types'
    else:
        to_exclude = set()

    for node_typename in all_nodes:
        if node_typename in to_exclude:
            continue

        node_ty = getattr(node, node_typename)
        if not issubclass(node_ty, ABC) and issubclass(
                node_ty, node.Node) and not fn(node_ty):
            warnings.warn(f'{name}: invalid for {node_typename}')


def assert_all_registered(func: singledispatch):
    expect_all_concrete_nodes(f'{func.__module__}.{func.__name__}',
                              lambda ty: ty in func.registry)
