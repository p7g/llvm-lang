from .node import Node
from .iter import iter_node


class Visitor:
    def visit(self, node: Node):
        typename = type(node).__name__
        method = getattr(self, f'visit_{typename}', self.generic_visit)
        method(node)

    def generic_visit(self, node: Node):
        for child in iter_node(node):
            self.visit(child)
