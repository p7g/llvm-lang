from .node import Node
from .iter import iter_node


class Visitor:
    def __init__(self):
        self._path = []

    def visit(self, node: Node):
        typename = type(node).__name__
        method = getattr(self, f'visit_{typename}', self.generic_visit)
        return method(node)

    def generic_visit(self, node: Node):
        for i, child in enumerate(iter_node(node)):
            self._path.append(i)
            yield self.visit(child)
            self._path.pop()

    def path(self):
        return tuple(self._path)
