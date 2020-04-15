from llvm_lang import types, errors


class Scope:
    def __init__(self):
        self.bindings = {}

    def has_binding(self, name: str) -> bool:
        return name in self.bindings

    def add_binding(self, name: str, typ: types.Type):
        if self.has_binding(name):
            raise errors.SyntaxError(f'Redeclaring binding {name}')
        self.bindings[name] = typ

    def get_binding(self, name: str) -> types.Type:
        return self.bindings[name]


class Scopes:
    def __init__(self):
        self.scopes = [Scope()]

    def push_scope(self):
        self.scopes.append(Scope())

    def pop_scope(self):
        self.scopes.pop()

    def add_binding(self, name: str, typ: types.Type):
        self.scopes[-1].add_binding(name, typ)

    def resolve_binding(self, name: str) -> types.Type:
        for scope in reversed(self.scopes):
            if scope.has_binding(name):
                return scope.get_binding(name)
        raise errors.ReferenceError(f'Unbound identifier {name}')
