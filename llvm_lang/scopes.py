from contextlib import contextmanager
from typing import Generic, Iterable, Optional, Tuple, TypeVar

from llvm_lang import errors

T_Scope = TypeVar('T_Scope')


class Scope(Generic[T_Scope]):
    def __init__(self, it: Optional[Iterable[Tuple[str, T_Scope]]] = None):
        self.bindings = dict(it or ())

    def has_binding(self, name: str) -> bool:
        return name in self.bindings

    def add_binding(self, name: str, typ: T_Scope):
        if self.has_binding(name):
            raise errors.SyntaxError(f'Redeclaring binding {name}')
        self.bindings[name] = typ

    def get_binding(self, name: str) -> T_Scope:
        return self.bindings[name]


T_Scopes = TypeVar('T_Scopes')


class Scopes(Generic[T_Scopes]):
    def __init__(self, it: Optional[Iterable[Tuple[str, T_Scopes]]] = None):
        self.scopes = [Scope[T_Scopes](it)]

    def push_scope(self):
        self.scopes.append(Scope[T_Scopes]())

    def pop_scope(self):
        self.scopes.pop()

    @contextmanager
    def new_scope(self):
        self.push_scope()
        yield
        self.pop_scope()

    def add_binding(self, name: str, typ: T_Scopes):
        self.scopes[-1].add_binding(name, typ)

    def has_binding(self, name: str):
        for scope in reversed(self.scopes):
            if scope.has_binding(name):
                return True
        return False

    def resolve_binding(self, name: str) -> T_Scopes:
        for scope in reversed(self.scopes):
            if scope.has_binding(name):
                return scope.get_binding(name)
        raise errors.ReferenceError(f'Unbound identifier {name}')
