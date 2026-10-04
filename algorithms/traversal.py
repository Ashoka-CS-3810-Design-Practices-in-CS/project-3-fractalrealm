
from errors import EmptyStructureError, InvalidInputError

ORDERS = ("pre", "in", "post")
_VISIT_LINE = {"pre": 2, "in": 4, "post": 6}   # lines in services/pseudocode.py


def traverse(tree, order, log):
    if order not in ORDERS:
        raise InvalidInputError("Traversal order must be one of: pre, in, post")
    if tree.root is None:
        raise EmptyStructureError("Tree is empty")

    state = tree.to_dict()          # the tree never changes during a traversal
    visited = []
    line = _VISIT_LINE[order]

    def visit(node):
        visited.append(node.value)
        log.add("visit", "Visit %d (%s-order position %d)" % (node.value, order, len(visited)),
                state, line=line, current=[node.value], visited=visited)

    def walk(node):
        if node is None:
            return
        if order == "pre":
            visit(node)
        walk(node.left)
        if order == "in":
            visit(node)
        walk(node.right)
        if order == "post":
            visit(node)

    walk(tree.root)
    log.add("visit", "%s-order traversal complete: %s" % (order.capitalize(), " → ".join(map(str, visited))),
            state, line=0, visited=visited)
    log.result = {"order": list(visited), "traversal": order}
    return log
