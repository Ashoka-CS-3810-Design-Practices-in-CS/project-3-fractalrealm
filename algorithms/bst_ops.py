
from errors import DuplicateValueError, NotFoundError
from models.bst import BSTNode


def _direction(value, node_value):
    if value == node_value:
        return "equal"
    return "%d < %d, go left" % (value, node_value) if value < node_value \
        else "%d > %d, go right" % (value, node_value)


def _replace_child(tree, parent, side, new_child):
    if parent is None:
        tree.root = new_child
    else:
        setattr(parent, side, new_child)


def insert(tree, value, log):
    """Insert ``value`` as a leaf. Raises DuplicateValueError for an existing key."""
    if tree.root is None:
        tree.root = BSTNode(value)
        log.add("insertNode", "Tree is empty: %d becomes the root" % value,
                tree.to_dict(), line=5, current=[value])
        log.result = {"inserted": value}
        return log

    node = tree.root
    path = []
    while True:
        path.append(node.value)
        log.add("compare", "Compare %d with %d: %s" % (value, node.value, _direction(value, node.value)),
                tree.to_dict(), line=2, current=[node.value], visited=path[:-1])
        if value == node.value:
            raise DuplicateValueError("%d is already in the tree (duplicate keys are not allowed)" % value)
        side = "left" if value < node.value else "right"
        child = getattr(node, side)
        if child is None:
            break
        node = child

    setattr(node, side, BSTNode(value))
    log.add("insertNode", "Empty %s slot found: insert %d as the %s child of %d" % (side, value, side, node.value),
            tree.to_dict(), line=5, current=[value], visited=path)
    log.result = {"inserted": value, "path": path}
    return log


def search(tree, target, log):
    """Search for ``target``; result holds ``found`` and the ``path`` taken."""
    node = tree.root
    path = []
    while node is not None:
        path.append(node.value)
        log.add("compare", "Compare %d with %d: %s" % (target, node.value, _direction(target, node.value)),
                tree.to_dict(), line=2, current=[node.value], visited=path[:-1])
        if target == node.value:
            log.add("found", "Found %d after %d comparison(s)" % (target, len(path)),
                    tree.to_dict(), line=3, current=[node.value], visited=path[:-1])
            log.result = {"found": True, "path": path}
            return log
        node = node.left if target < node.value else node.right

    log.add("notFound", "Reached an empty child: %d is not in the tree" % target,
            tree.to_dict(), line=5, visited=path)
    log.result = {"found": False, "path": path}
    return log


def delete(tree, value, log):
    """Delete ``value`` handling 0, 1 and 2 children. Raises NotFoundError if missing."""
    parent, side, node = None, None, tree.root
    path = []
    while node is not None:
        path.append(node.value)
        log.add("compare", "Compare %d with %d: %s" % (value, node.value, _direction(value, node.value)),
                tree.to_dict(), line=0, current=[node.value], visited=path[:-1])
        if value == node.value:
            break
        parent, side = node, ("left" if value < node.value else "right")
        node = getattr(node, side)

    if node is None:
        raise NotFoundError("%d is not in the tree" % value)

    parent_ids = [parent.value] if parent else []

    if node.left is None and node.right is None:
        _replace_child(tree, parent, side, None)
        log.add("removeNode", "%d is a leaf: remove it" % value,
                tree.to_dict(), line=2, current=parent_ids, visited=path[:-1])
    elif node.left is None or node.right is None:
        child = node.left or node.right
        _replace_child(tree, parent, side, child)
        log.add("removeNode", "%d has one child: replace it with %d" % (value, child.value),
                tree.to_dict(), line=3, current=[child.value], visited=path[:-1])
    else:
        succ_parent, succ = node, node.right
        log.add("visit", "%d has two children: find the in-order successor (smallest value in its right subtree). Start at %d"
                % (value, succ.value),
                tree.to_dict(), line=4, current=[succ.value], visited=path)
        while succ.left is not None:
            succ_parent, succ = succ, succ.left
            log.add("visit", "Go left to %d" % succ.value,
                    tree.to_dict(), line=4, current=[succ.value], visited=path)
        log.add("found", "Successor is %d (no left child)" % succ.value,
                tree.to_dict(), line=4, current=[succ.value], visited=path)

        node.value = succ.value
        log.add("swap", "Copy successor value %d into the node being deleted" % succ.value,
                tree.to_dict(), line=5, current=[succ.value], visited=path)

        if succ_parent is node:
            node.right = succ.right
        else:
            succ_parent.left = succ.right
        log.add("removeNode", "Remove the original successor node %d from the right subtree" % succ.value,
                tree.to_dict(), line=6, current=[node.value], visited=path)

    log.result = {"deleted": value}
    return log
