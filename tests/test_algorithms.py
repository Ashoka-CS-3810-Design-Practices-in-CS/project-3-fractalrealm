import heapq
import random
import unittest

import networkx as nx

from algorithms import bst_ops, heap_ops, linear_ops, traversal
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.step_log import StepLog
from errors import (DuplicateValueError, EmptyStructureError, InvalidInputError,
                    NotFoundError)
from models.bst import BST
from models.graph import Graph
from models.priority_queue import PriorityQueue
from models.queue import Queue
from models.stack import Stack


def build_bst(values):
    tree = BST()
    for v in values:
        bst_ops.insert(tree, v, StepLog("bst"))
    return tree


def random_graph(rng, n, m):
    names = [chr(ord("A") + i) for i in range(n)]
    g = Graph()
    for v in names:
        g.add_vertex(v)
    pairs = [(names[i], names[j]) for i in range(n) for j in range(i + 1, n)]
    for u, v in rng.sample(pairs, min(m, len(pairs))):
        g.add_edge(u, v)
    return g


def reference_graph(g):
    """networkx graph with sorted adjacency, so networkx visits neighbours in our order."""
    d = g.to_dict()
    h = nx.Graph()
    h.add_nodes_from(d["vertices"])
    h.add_edges_from(sorted(tuple(sorted(e)) for e in d["edges"]))
    return h


class TestBSTOps(unittest.TestCase):
    def test_insert_matches_sorted_set(self):
        rng = random.Random(1)
        values = rng.sample(range(-50, 50), 30)
        tree = build_bst(values)
        self.assertEqual(tree.in_order_values(), sorted(values))

    def test_insert_logs_comparisons_then_insert(self):
        tree = build_bst([50, 30, 70])
        log = StepLog("bst")
        bst_ops.insert(tree, 20, log)
        self.assertEqual([s["action"] for s in log.steps], ["compare", "compare", "insertNode"])
        self.assertIn(20, tree.in_order_values())
        self.assertEqual(log.steps[-1]["structureState"], tree.to_dict())

    def test_insert_duplicate(self):
        tree = build_bst([5])
        with self.assertRaises(DuplicateValueError):
            bst_ops.insert(tree, 5, StepLog("bst"))
        self.assertEqual(tree.in_order_values(), [5])

    def test_search_path(self):
        tree = build_bst([50, 30, 70, 20, 40, 60, 80])
        log = StepLog("bst")
        bst_ops.search(tree, 20, log)
        self.assertTrue(log.result["found"])
        self.assertEqual(log.result["path"], [50, 30, 20])      # the example from the A1 report
        self.assertEqual(log.steps[-1]["action"], "found")

    def test_search_missing(self):
        tree = build_bst([50, 30, 70])
        log = StepLog("bst")
        bst_ops.search(tree, 99, log)
        self.assertFalse(log.result["found"])
        self.assertEqual(log.steps[-1]["action"], "notFound")

    def test_delete_leaf(self):
        tree = build_bst([50, 30, 70, 20])
        bst_ops.delete(tree, 20, StepLog("bst"))
        self.assertEqual(tree.in_order_values(), [30, 50, 70])
        self.assertIsNone(tree.root.left.left)

    def test_delete_node_with_one_child(self):
        tree = build_bst([50, 30, 70, 20])          # 30 has only a left child (20)
        bst_ops.delete(tree, 30, StepLog("bst"))
        self.assertEqual(tree.in_order_values(), [20, 50, 70])
        self.assertEqual(tree.root.left.value, 20)

    def test_delete_two_children_uses_successor(self):
        tree = build_bst([50, 30, 70, 60, 80])
        log = StepLog("bst")
        bst_ops.delete(tree, 50, log)
        self.assertEqual(tree.root.value, 60)                    # in-order successor
        self.assertEqual(tree.in_order_values(), [30, 60, 70, 80])
        self.assertIn("swap", [s["action"] for s in log.steps])

    def test_delete_root_single_node(self):
        tree = build_bst([5])
        bst_ops.delete(tree, 5, StepLog("bst"))
        self.assertTrue(tree.is_empty())

    def test_delete_random_matches_set(self):
        rng = random.Random(7)
        values = rng.sample(range(100), 40)
        tree = build_bst(values)
        remaining = set(values)
        for v in rng.sample(values, 25):
            bst_ops.delete(tree, v, StepLog("bst"))
            remaining.discard(v)
            self.assertEqual(tree.in_order_values(), sorted(remaining))

    def test_delete_missing(self):
        tree = build_bst([1, 2, 3])
        with self.assertRaises(NotFoundError):
            bst_ops.delete(tree, 9, StepLog("bst"))


class TestTraversal(unittest.TestCase):
    def setUp(self):
        self.tree = build_bst([50, 30, 70, 20, 40, 60, 80])

    def run_order(self, order):
        log = StepLog("bst")
        traversal.traverse(self.tree, order, log)
        return log

    def test_orders(self):
        self.assertEqual(self.run_order("pre").result["order"], [50, 30, 20, 40, 70, 60, 80])
        self.assertEqual(self.run_order("in").result["order"], [20, 30, 40, 50, 60, 70, 80])
        self.assertEqual(self.run_order("post").result["order"], [20, 40, 30, 60, 80, 70, 50])

    def test_each_node_visited_once(self):
        log = self.run_order("in")
        visits = [s for s in log.steps if s["highlight"]["current"]]
        self.assertEqual(len(visits), 7)

    def test_errors(self):
        with self.assertRaises(EmptyStructureError):
            traversal.traverse(BST(), "in", StepLog("bst"))
        with self.assertRaises(InvalidInputError):
            traversal.traverse(self.tree, "level", StepLog("bst"))


class TestGraphTraversal(unittest.TestCase):
    def test_fixed_example(self):
        g = Graph.from_dict({"vertices": list("ABCDE"),
                             "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"], ["C", "E"]]})
        log = StepLog("graph")
        bfs(g, "A", None, log)
        self.assertEqual(log.result["order"], ["A", "B", "C", "D", "E"])
        log = StepLog("graph")
        dfs(g, "A", None, log)
        self.assertEqual(log.result["order"], ["A", "B", "D", "C", "E"])

    def test_against_networkx(self):
        rng = random.Random(3)
        for _ in range(40):
            n = rng.randint(1, 12)
            g = random_graph(rng, n, rng.randint(0, n * 2))
            ref = reference_graph(g)
            src = rng.choice(g.vertices())
            log = StepLog("graph")
            bfs(g, src, None, log)
            self.assertEqual(log.result["order"], list(nx.bfs_tree(ref, src)))
            log = StepLog("graph")
            dfs(g, src, None, log)
            self.assertEqual(log.result["order"], list(nx.dfs_preorder_nodes(ref, src)))

    def test_bfs_path_is_shortest(self):
        rng = random.Random(5)
        for _ in range(40):
            n = rng.randint(2, 12)
            g = random_graph(rng, n, rng.randint(1, n * 2))
            ref = reference_graph(g)
            src, dst = rng.sample(g.vertices(), 2)
            log = StepLog("graph")
            bfs(g, src, dst, log)
            if nx.has_path(ref, src, dst):
                self.assertTrue(log.result["found"])
                self.assertEqual(log.result["distance"], nx.shortest_path_length(ref, src, dst))
                path = log.result["path"]
                self.assertEqual((path[0], path[-1]), (src, dst))
                self.assertTrue(all(ref.has_edge(a, b) for a, b in zip(path, path[1:])))
            else:
                self.assertFalse(log.result["found"])
                self.assertEqual(log.steps[-1]["action"], "notFound")

    def test_dfs_path_is_valid(self):
        g = Graph.from_dict({"vertices": list("ABCD"), "edges": [["A", "B"], ["B", "C"], ["A", "D"]]})
        log = StepLog("graph")
        dfs(g, "A", "C", log)
        self.assertEqual(log.result["path"], ["A", "B", "C"])

    def test_source_equals_destination(self):
        g = Graph.from_dict({"vertices": ["A"], "edges": []})
        for algo in (bfs, dfs):
            log = StepLog("graph")
            algo(g, "A", "A", log)
            self.assertEqual(log.result["path"], ["A"])

    def test_queue_and_stack_contents_recorded(self):
        g = Graph.from_dict({"vertices": list("ABC"), "edges": [["A", "B"], ["A", "C"]]})
        log = StepLog("graph")
        bfs(g, "A", None, log)
        self.assertEqual(log.steps[0]["aux"], {"queue": ["A"]})
        self.assertTrue(all("queue" in s["aux"] for s in log.steps))
        log = StepLog("graph")
        dfs(g, "A", None, log)
        self.assertEqual(log.steps[0]["aux"], {"stack": ["A"]})
        self.assertEqual(log.steps[-1]["aux"], {"stack": []})

    def test_every_edge_is_explored(self):
        g = Graph.from_dict({"vertices": list("ABCD"), "edges": [["A", "B"], ["B", "C"], ["C", "A"], ["C", "D"]]})
        log = StepLog("graph")
        bfs(g, "A", None, log)
        explored = {tuple(sorted(s["highlight"]["edges"][0])) for s in log.steps if s["action"] == "explore"}
        self.assertEqual(explored, {tuple(e) for e in g.to_dict()["edges"]})


class TestHeapOps(unittest.TestCase):
    def test_insert_keeps_heap(self):
        rng = random.Random(9)
        pq = PriorityQueue()
        for v in [rng.randint(-20, 20) for _ in range(40)]:
            heap_ops.insert(pq, v, StepLog("heap"))
            self.assertTrue(pq.is_valid_heap())

    def test_extract_matches_heapq(self):
        rng = random.Random(11)
        values = [rng.randint(-50, 50) for _ in range(30)]
        pq = PriorityQueue()
        ref = []
        for v in values:
            heap_ops.insert(pq, v, StepLog("heap"))
            heapq.heappush(ref, v)
        while not pq.is_empty():
            log = StepLog("heap")
            heap_ops.extract_min(pq, log)
            self.assertEqual(log.result["min"], heapq.heappop(ref))
            self.assertTrue(pq.is_valid_heap())

    def test_extract_empty(self):
        with self.assertRaises(EmptyStructureError):
            heap_ops.extract_min(PriorityQueue(), StepLog("heap"))

    def test_swaps_are_logged(self):
        pq = PriorityQueue([5, 7, 9])
        log = StepLog("heap")
        heap_ops.insert(pq, 1, log)            # 1 must travel to the root: two swaps
        self.assertEqual([s["action"] for s in log.steps].count("swap"), 2)
        self.assertEqual(pq.array[0], 1)


class TestLinearOps(unittest.TestCase):
    def test_stack_sequence(self):
        s = Stack()
        linear_ops.stack_push(s, 1, StepLog("stack"))
        linear_ops.stack_push(s, 2, StepLog("stack"))
        log = StepLog("stack")
        linear_ops.stack_pop(s, log)
        self.assertEqual(log.result["popped"], 2)
        self.assertEqual(len(log.steps), 2)                      # highlight, then remove
        self.assertEqual(s.to_dict(), {"items": [1]})

    def test_stack_pop_empty(self):
        with self.assertRaises(EmptyStructureError):
            linear_ops.stack_pop(Stack(), StepLog("stack"))

    def test_queue_sequence(self):
        q = Queue()
        for v in (1, 2, 3):
            linear_ops.queue_enqueue(q, v, StepLog("queue"))
        log = StepLog("queue")
        linear_ops.queue_dequeue(q, log)
        self.assertEqual(log.result["dequeued"], 1)
        self.assertEqual(q.to_dict(), {"items": [2, 3]})
        log = StepLog("queue")
        linear_ops.queue_rear(q, log)
        self.assertEqual(log.result["value"], 3)

    def test_is_empty(self):
        log = StepLog("queue")
        linear_ops.queue_is_empty(Queue(), log)
        self.assertTrue(log.result["empty"])


if __name__ == "__main__":
    unittest.main()
