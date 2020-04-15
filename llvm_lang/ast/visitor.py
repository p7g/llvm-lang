from .node import Node
from .iter import iter_node


class Visitor:
    def __init__(self):
        self._path = []

    def visit(self, node: Node):
        for typ in type(node).__mro__:
            typename = typ.__name__
            method_name = f'visit_{typename}'
            method = getattr(self, method_name, None)
            if method:
                return method(node)
        return self.generic_visit(node)

    def generic_visit(self, node: Node):
        results = []
        for i, child in enumerate(iter_node(node)):
            self._path.append(i)
            results.append(self.visit(child))
            self._path.pop()
        return results

    def path(self):
        return tuple(self._path)
