import unittest

from errors import (DuplicateValueError, EmptyStructureError, InvalidInputError,
                    NotFoundError, SizeLimitError)
from models.bst import BST
from models.graph import Graph
from models.priority_queue import PriorityQueue
from models.queue import Queue
from models.stack import Stack


class TestBST(unittest.TestCase):
    def test_round_trip(self):
        data = {"value": 50, "left": {"value": 30, "left": None, "right": None}, "right": None}
        tree = BST.from_dict(data)
        self.assertEqual(tree.to_dict(), data)
        self.assertEqual(tree.size(), 2)
        self.assertEqual(tree.height(), 2)
        self.assertEqual(tree.in_order_values(), [30, 50])

    def test_empty(self):
        tree = BST.from_dict(None)
        self.assertTrue(tree.is_empty())
        self.assertIsNone(tree.to_dict())
        self.assertEqual(tree.height(), 0)

    def test_rejects_ordering_violation(self):
        bad = {"value": 10, "left": {"value": 20, "left": None, "right": None}, "right": None}
        with self.assertRaises(InvalidInputError):
            BST.from_dict(bad)

    def test_rejects_non_integer(self):
        with self.assertRaises(InvalidInputError):
            BST.from_dict({"value": "x"})

    def test_size_limit(self):
        node = None
        for v in range(51, 0, -1):
            node = {"value": v, "left": None, "right": node}
        with self.assertRaises(SizeLimitError):
            BST.from_dict(node)


class TestGraph(unittest.TestCase):
    def test_round_trip_sorted(self):
        g = Graph.from_dict({"vertices": ["B", "A", "C"], "edges": [["C", "A"], ["A", "B"]]})
        self.assertEqual(g.to_dict(), {"vertices": ["A", "B", "C"], "edges": [["A", "B"], ["A", "C"]]})
        self.assertEqual(g.neighbors("A"), ["B", "C"])

    def test_duplicate_vertex(self):
        g = Graph()
        g.add_vertex("A")
        with self.assertRaises(DuplicateValueError):
            g.add_vertex("A")

    def test_edge_to_missing_vertex(self):
        g = Graph()
        g.add_vertex("A")
        with self.assertRaises(NotFoundError):
            g.add_edge("A", "Z")

    def test_self_loop_and_duplicate_edge(self):
        g = Graph.from_dict({"vertices": ["A", "B"], "edges": [["A", "B"]]})
        with self.assertRaises(InvalidInputError):
            g.add_edge("A", "A")
        with self.assertRaises(DuplicateValueError):
            g.add_edge("B", "A")

    def test_remove_vertex_removes_edges(self):
        g = Graph.from_dict({"vertices": ["A", "B"], "edges": [["A", "B"]]})
        g.remove_vertex("A")
        self.assertEqual(g.to_dict(), {"vertices": ["B"], "edges": []})

    def test_vertex_limit(self):
        g = Graph()
        for i in range(50):
            g.add_vertex("v%d" % i)
        with self.assertRaises(SizeLimitError):
            g.add_vertex("extra")

    def test_blank_label(self):
        with self.assertRaises(InvalidInputError):
            Graph().add_vertex("  ")


class TestPriorityQueue(unittest.TestCase):
    def test_peek_empty(self):
        with self.assertRaises(EmptyStructureError):
            PriorityQueue().peek()

    def test_rejects_invalid_heap(self):
        with self.assertRaises(InvalidInputError):
            PriorityQueue.from_dict({"array": [5, 1]})

    def test_index_helpers(self):
        self.assertEqual(PriorityQueue.parent(4), 1)
        self.assertEqual(PriorityQueue.children(1), (3, 4))


class TestStackQueue(unittest.TestCase):
    def test_stack_lifo(self):
        s = Stack()
        s.push(1)
        s.push(2)
        self.assertEqual(s.peek(), 2)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)
        self.assertTrue(s.is_empty())

    def test_stack_empty_errors(self):
        with self.assertRaises(EmptyStructureError):
            Stack().pop()
        with self.assertRaises(EmptyStructureError):
            Stack().peek()

    def test_queue_fifo(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        self.assertEqual((q.front(), q.rear()), (1, 2))
        self.assertEqual(q.dequeue(), 1)
        self.assertEqual(q.dequeue(), 2)
        self.assertTrue(q.is_empty())

    def test_queue_empty_errors(self):
        for fn in (Queue().dequeue, Queue().front, Queue().rear):
            with self.assertRaises(EmptyStructureError):
                fn()

    def test_round_trip(self):
        self.assertEqual(Stack.from_dict({"items": [1, 2]}).to_dict(), {"items": [1, 2]})
        self.assertEqual(Queue.from_dict({"items": [1, 2]}).to_dict(), {"items": [1, 2]})

    def test_rejects_non_integers(self):
        with self.assertRaises(InvalidInputError):
            Stack.from_dict({"items": ["a"]})


if __name__ == "__main__":
    unittest.main()
