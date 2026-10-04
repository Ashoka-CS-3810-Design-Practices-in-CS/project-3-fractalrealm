
from algorithms import bst_ops, traversal
from algorithms.step_log import StepLog
from config import MAX_NODES
from errors import EmptyStructureError, SizeLimitError
from models.bst import BST
from services.common import build_response, parse_int_value


def _load(payload):
    return BST.from_dict(payload.get("tree"))


def insert(payload):
    tree = _load(payload)
    value = parse_int_value(payload.get("value"))
    if tree.size() >= MAX_NODES:
        raise SizeLimitError(
            "The tree is too large to visualise clearly (limit: %d nodes); further insertion is blocked" % MAX_NODES)
    log = StepLog("bst")
    bst_ops.insert(tree, value, log)
    return build_response(log, tree.to_dict(), "bst.insert")


def delete(payload):
    tree = _load(payload)
    if tree.is_empty():
        raise EmptyStructureError("Tree is empty")
    value = parse_int_value(payload.get("value"))
    log = StepLog("bst")
    bst_ops.delete(tree, value, log)
    return build_response(log, tree.to_dict(), "bst.delete")


def search(payload):
    tree = _load(payload)
    if tree.is_empty():
        raise EmptyStructureError("Tree is empty")
    target = parse_int_value(payload.get("value"), "search value")
    log = StepLog("bst")
    bst_ops.search(tree, target, log)
    return build_response(log, tree.to_dict(), "bst.search")


def traverse(payload):
    tree = _load(payload)
    log = StepLog("bst")
    traversal.traverse(tree, payload.get("order", "in"), log)
    return build_response(log, tree.to_dict(), "bst.traverse")
