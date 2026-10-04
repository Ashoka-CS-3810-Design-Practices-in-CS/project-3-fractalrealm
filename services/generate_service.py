"""FR5: random test-case generation."""
import random

from algorithms import bst_ops, heap_ops, linear_ops
from algorithms.step_log import StepLog
from config import MAX_EDGES, MAX_NODES
from errors import InvalidInputError, SizeLimitError
from models.bst import BST
from models.graph import Graph
from models.priority_queue import PriorityQueue
from models.queue import Queue
from models.stack import Stack
from services.common import parse_int_value, single_step_response

DISTRIBUTIONS = ("random", "ascending", "descending")
STRUCTURES = ("bst", "heap", "stack", "queue", "graph")


def _vertex_name(i):
    """A, B, ... Z, A1, B1, ... (50 vertices at most)."""
    letter = chr(ord("A") + i % 26)
    return letter if i < 26 else "%s%d" % (letter, i // 26)


def _parse_count(raw, name="number of values"):
    count = parse_int_value(raw, name)
    if count < 1:
        raise InvalidInputError("The %s must be at least 1" % name)
    if count > MAX_NODES:
        raise SizeLimitError("At most %d nodes / vertices can be generated" % MAX_NODES)
    return count


def _make_values(count, lo, hi, distribution, unique, rng):
    if lo > hi:
        raise InvalidInputError("The minimum of the range must not exceed the maximum")
    if unique:
        if hi - lo + 1 < count:
            raise InvalidInputError(
                "The range %d..%d has only %d distinct values, but %d are needed" % (lo, hi, hi - lo + 1, count))
        values = rng.sample(range(lo, hi + 1), count)
    else:
        values = [rng.randint(lo, hi) for _ in range(count)]
    if distribution == "ascending":
        values.sort()
    elif distribution == "descending":
        values.sort(reverse=True)
    return values


def generate(payload, rng=None):
    rng = rng or random
    structure = payload.get("structure")
    if structure not in STRUCTURES:
        raise InvalidInputError("Unknown structure: %r" % (structure,))
    distribution = payload.get("distribution", "random")
    if distribution not in DISTRIBUTIONS:
        raise InvalidInputError("Distribution must be one of: %s" % ", ".join(DISTRIBUTIONS))
    count = _parse_count(payload.get("count"), "number of vertices" if structure == "graph" else "number of values")

    key = "generate." + structure
    if structure == "graph":
        return _generate_graph(payload, count, key, rng)

    lo = parse_int_value(payload.get("min", 1), "minimum")
    hi = parse_int_value(payload.get("max", 99), "maximum")
    values = _make_values(count, lo, hi, distribution, unique=(structure == "bst"), rng=rng)
    scratch = StepLog(structure)               # the build steps are not animated

    if structure == "bst":
        tree = BST()
        for v in values:
            bst_ops.insert(tree, v, scratch)
        state = tree.to_dict()
    elif structure == "heap":
        pq = PriorityQueue()
        for v in values:
            heap_ops.insert(pq, v, scratch)
        state = pq.to_dict()
    elif structure == "stack":
        stack = Stack()
        for v in values:
            linear_ops.stack_push(stack, v, scratch)
        state = stack.to_dict()
    else:
        queue = Queue()
        for v in values:
            linear_ops.queue_enqueue(queue, v, scratch)
        state = queue.to_dict()

    return single_step_response(
        structure, "insertNode",
        "Generated %d %s value(s) in the range %d..%d: %s" % (count, distribution, lo, hi, values),
        state, key, result={"values": values})


def _generate_graph(payload, count, key, rng):
    max_possible = count * (count - 1) // 2
    edge_count = parse_int_value(payload.get("edges", min(count, max_possible)), "number of edges")
    if edge_count < 0:
        raise InvalidInputError("The number of edges cannot be negative")
    if edge_count > max_possible:
        raise InvalidInputError("%d vertices can have at most %d edges" % (count, max_possible))
    if edge_count > MAX_EDGES:
        raise SizeLimitError("At most %d edges can be generated" % MAX_EDGES)

    graph = Graph()
    names = [_vertex_name(i) for i in range(count)]
    for n in names:
        graph.add_vertex(n)
    all_pairs = [(names[i], names[j]) for i in range(count) for j in range(i + 1, count)]
    for u, v in rng.sample(all_pairs, edge_count):
        graph.add_edge(u, v)
    state = graph.to_dict()
    return single_step_response(
        "graph", "insertNode",
        "Generated a graph with %d vertices and %d edges" % (count, edge_count),
        state, key, result={"vertices": count, "edges": edge_count})
