"""Binary Search Tree model 

JSON form:  {"value": 50, "left": {...}, "right": null}   (None = empty tree)
"""
from config import MAX_NODES
from errors import InvalidInputError, SizeLimitError


class BSTNode:
    __slots__ = ("value", "left", "right")

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def to_dict(self):
        return {
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }


class BST:
    """Holds the root only; insert / delete / search live in algorithms/bst_ops.py."""

    def __init__(self, root=None):
        self.root = root



    @classmethod
    def from_dict(cls, data):
        counter = [0]
        root = cls._build(data, None, None, counter)
        return cls(root)

    @staticmethod
    def _build(data, low, high, counter):
        """Rebuild nodes recursively, validating the BST invariant on the way."""
        if data is None:
            return None
        if not isinstance(data, dict):
            raise InvalidInputError("Malformed tree: each node must be an object")
        value = data.get("value")
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidInputError("Malformed tree: node values must be integers")
        if (low is not None and value <= low) or (high is not None and value >= high):
            raise InvalidInputError("Malformed tree: BST ordering is violated")
        counter[0] += 1
        if counter[0] > MAX_NODES:
            raise SizeLimitError(
                "The tree is too large to visualise clearly (limit: %d nodes)" % MAX_NODES
            )
        node = BSTNode(value)
        node.left = BST._build(data.get("left"), low, value, counter)
        node.right = BST._build(data.get("right"), value, high, counter)
        return node

    def to_dict(self):
        return self.root.to_dict() if self.root else None


 
    def is_empty(self):
        return self.root is None

    def size(self):
        def count(node):
            return 0 if node is None else 1 + count(node.left) + count(node.right)
        return count(self.root)

    def height(self):
        """Number of levels (empty tree = 0, single node = 1)."""
        def h(node):
            return 0 if node is None else 1 + max(h(node.left), h(node.right))
        return h(self.root)

    def in_order_values(self):
        out = []

        def walk(node):
            if node is None:
                return
            walk(node.left)
            out.append(node.value)
            walk(node.right)

        walk(self.root)
        return out

    def contains(self, value):
        node = self.root
        while node is not None:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False
