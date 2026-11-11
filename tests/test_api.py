"""End-to-end tests of the Flask routes + service layer (the stateless request flow of A2, 5.2)."""
import random
import unittest

from app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def post(self, path, body):
        res = self.client.post(path, json=body)
        return res.status_code, res.get_json()


class TestBstApi(ApiTestCase):
    def test_insert_flow_and_response_shape(self):
        tree = None
        for v in (50, 30, 70):
            status, data = self.post("/api/bst/insert", {"tree": tree, "value": v})
            self.assertEqual(status, 200)
            tree = data["finalState"]
        self.assertEqual(set(data), {"operation", "steps", "finalState", "complexity", "pseudocode", "result"})
        self.assertEqual(data["complexity"]["worst"], "O(n)")
        self.assertEqual(data["complexity"]["space"], "O(h)")
        self.assertTrue(len(data["steps"]) >= 2)
        self.assertEqual(data["steps"][-1]["structureState"], data["finalState"])

    def test_string_value_is_parsed(self):
        status, data = self.post("/api/bst/insert", {"tree": None, "value": " 12 "})
        self.assertEqual(status, 200)
        self.assertEqual(data["finalState"]["value"], 12)

    def test_errors_leave_a_clean_message(self):
        _, tree = self.post("/api/bst/insert", {"tree": None, "value": 5})
        tree = tree["finalState"]
        for body, fragment in [
            ({"tree": tree, "value": 5}, "already"),            # duplicate key
            ({"tree": tree, "value": "abc"}, "whole number"),   # bad input
            ({"tree": tree, "value": ""}, "Please enter"),      # missing input
            ({"tree": tree, "value": 100000}, "between"),       # out of range
        ]:
            status, data = self.post("/api/bst/insert", body)
            self.assertEqual(status, 400)
            self.assertIn(fragment, data["error"])
            self.assertNotIn("steps", data)

    def test_empty_tree_errors(self):
        for path in ("delete", "search"):
            status, data = self.post("/api/bst/" + path, {"tree": None, "value": 1})
            self.assertEqual(status, 400)
            self.assertIn("empty", data["error"].lower())
        status, data = self.post("/api/bst/traverse", {"tree": None, "order": "in"})
        self.assertEqual(status, 400)

    def test_delete_missing_value(self):
        _, t = self.post("/api/bst/insert", {"tree": None, "value": 5})
        status, data = self.post("/api/bst/delete", {"tree": t["finalState"], "value": 9})
        self.assertEqual(status, 400)
        self.assertIn("not in the tree", data["error"])

    def test_size_limit_blocks_insert(self):
        tree = None
        for v in range(25):
            status, data = self.post("/api/bst/insert", {"tree": tree, "value": v})
            self.assertEqual(status, 200)
            tree = data["finalState"]
        status, data = self.post("/api/bst/insert", {"tree": tree, "value": 99})
        self.assertEqual(status, 400)
        self.assertIn("too large", data["error"])

    def test_traverse(self):
        tree = None
        for v in (2, 1, 3):
            tree = self.post("/api/bst/insert", {"tree": tree, "value": v})[1]["finalState"]
        status, data = self.post("/api/bst/traverse", {"tree": tree, "order": "pre"})
        self.assertEqual(data["result"]["order"], [2, 1, 3])

    def test_malformed_body(self):
        res = self.client.post("/api/bst/insert", data="not json", content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())


class TestGraphApi(ApiTestCase):
    def build(self):
        g = {"vertices": [], "edges": []}
        for v in "ABCD":
            g = self.post("/api/graph/add_vertex", {"graph": g, "vertex": v})[1]["finalState"]
        for u, v in (("A", "B"), ("A", "C"), ("B", "D")):
            g = self.post("/api/graph/add_edge", {"graph": g, "u": u, "v": v})[1]["finalState"]
        return g

    def test_edit_and_traverse(self):
        g = self.build()
        status, data = self.post("/api/graph/bfs", {"graph": g, "source": "A"})
        self.assertEqual(status, 200)
        self.assertEqual(data["result"]["order"], ["A", "B", "C", "D"])
        self.assertEqual(data["complexity"]["worst"], "O(V + E)")
        status, data = self.post("/api/graph/dfs", {"graph": g, "source": "A", "destination": "D"})
        self.assertEqual(data["result"]["path"], ["A", "B", "D"])

    def test_remove_edge_and_vertex(self):
        g = self.build()
        g = self.post("/api/graph/remove_edge", {"graph": g, "u": "A", "v": "B"})[1]["finalState"]
        self.assertNotIn(["A", "B"], g["edges"])
        g = self.post("/api/graph/remove_vertex", {"graph": g, "vertex": "B"})[1]["finalState"]
        self.assertNotIn("B", g["vertices"])
        self.assertTrue(all("B" not in e for e in g["edges"]))

    def test_validation_errors(self):
        g = self.build()
        cases = [
            ("/api/graph/add_vertex", {"graph": g, "vertex": "A"}, "already exists"),
            ("/api/graph/add_edge", {"graph": g, "u": "A", "v": "Z"}, "not in the graph"),
            ("/api/graph/add_edge", {"graph": g, "u": "A", "v": "B"}, "already exists"),
            ("/api/graph/bfs", {"graph": g, "source": "Z"}, "not in the graph"),
            ("/api/graph/bfs", {"graph": g}, "source"),
            ("/api/graph/dfs", {"graph": g, "source": "A", "destination": "Q"}, "Destination"),
            ("/api/graph/bfs", {"graph": {"vertices": [], "edges": []}, "source": "A"}, "empty"),
        ]
        for path, body, fragment in cases:
            status, data = self.post(path, body)
            self.assertEqual(status, 400, path)
            self.assertIn(fragment, data["error"])

    def test_compare_returns_both_logs(self):
        status, data = self.post("/api/graph/compare", {"graph": self.build(), "source": "A"})
        self.assertEqual(status, 200)
        self.assertEqual(data["bfs"]["operation"], "graph.bfs")
        self.assertEqual(data["dfs"]["operation"], "graph.dfs")
        self.assertIn("queue", data["bfs"]["steps"][0]["aux"])
        self.assertIn("stack", data["dfs"]["steps"][0]["aux"])


class TestLinearAndHeapApi(ApiTestCase):
    def test_stack(self):
        s = {"items": []}
        status, data = self.post("/api/stack/pop", {"stack": s})
        self.assertEqual((status, data["error"]), (400, "Stack is empty"))
        for v in (1, 2):
            s = self.post("/api/stack/push", {"stack": s, "value": v})[1]["finalState"]
        status, data = self.post("/api/stack/pop", {"stack": s})
        self.assertEqual(data["finalState"], {"items": [1]})
        self.assertEqual(data["result"]["popped"], 2)
        self.assertEqual(self.post("/api/stack/is_empty", {"stack": s})[1]["result"]["empty"], False)

    def test_queue(self):
        q = {"items": []}
        for path in ("dequeue", "front", "rear"):
            status, data = self.post("/api/queue/" + path, {"queue": q})
            self.assertEqual((status, data["error"]), (400, "Queue is empty"))
        for v in (1, 2, 3):
            q = self.post("/api/queue/enqueue", {"queue": q, "value": v})[1]["finalState"]
        self.assertEqual(self.post("/api/queue/front", {"queue": q})[1]["result"]["value"], 1)
        self.assertEqual(self.post("/api/queue/rear", {"queue": q})[1]["result"]["value"], 3)
        self.assertEqual(self.post("/api/queue/dequeue", {"queue": q})[1]["finalState"], {"items": [2, 3]})

    def test_heap(self):
        h = {"array": []}
        status, data = self.post("/api/heap/extract_min", {"heap": h})
        self.assertEqual(status, 400)
        for v in (5, 3, 8, 1):
            h = self.post("/api/heap/insert", {"heap": h, "value": v})[1]["finalState"]
        self.assertEqual(h["array"][0], 1)
        self.assertEqual(self.post("/api/heap/peek", {"heap": h})[1]["result"]["value"], 1)
        data = self.post("/api/heap/extract_min", {"heap": h})[1]
        self.assertEqual(data["result"]["min"], 1)
        self.assertEqual(data["finalState"]["array"][0], 3)

    def test_invalid_state_is_rejected_not_crashing(self):
        status, data = self.post("/api/stack/push", {"stack": {"items": "oops"}, "value": 1})
        self.assertEqual(status, 400)
        status, data = self.post("/api/heap/insert", {"heap": {"array": [9, 1]}, "value": 1})
        self.assertEqual(status, 400)


class TestGenerateAndReference(ApiTestCase):
    def test_generate_each_structure(self):
        for structure, key in (("bst", None), ("heap", "array"), ("stack", "items"), ("queue", "items")):
            status, data = self.post("/api/generate", {"structure": structure, "count": 12, "min": 1, "max": 99})
            self.assertEqual(status, 200, structure)
            state = data["finalState"]
            values = state if key is None else state[key]
            self.assertTrue(values)
        status, data = self.post("/api/generate", {"structure": "graph", "count": 6, "edges": 7})
        self.assertEqual(len(data["finalState"]["vertices"]), 6)
        self.assertEqual(len(data["finalState"]["edges"]), 7)

    def test_ascending_bst_is_a_chain(self):
        _, data = self.post("/api/generate", {"structure": "bst", "count": 8, "min": 1, "max": 50,
                                              "distribution": "ascending"})
        node, depth = data["finalState"], 0
        while node:
            self.assertIsNone(node["left"])
            node, depth = node["right"], depth + 1
        self.assertEqual(depth, 8)

    def test_generate_validation(self):
        cases = [
            ({"structure": "bst", "count": 5, "min": 10, "max": 1}, "minimum"),
            ({"structure": "bst", "count": 20, "min": 1, "max": 5}, "distinct"),
            ({"structure": "bst", "count": 26}, "At most"),
            ({"structure": "bst", "count": 0}, "at least"),
            ({"structure": "heap", "count": 5, "distribution": "zigzag"}, "Distribution"),
            ({"structure": "tree", "count": 5}, "Unknown"),
            ({"structure": "graph", "count": 3, "edges": 9}, "at most"),
        ]
        for body, fragment in cases:
            status, data = self.post("/api/generate", body)
            self.assertEqual(status, 400, body)
            self.assertIn(fragment, data["error"])

    def test_reference_covers_every_operation(self):
        res = self.client.get("/api/reference").get_json()
        self.assertEqual(set(res["complexity"]), set(res["pseudocode"]))
        for entry in res["complexity"].values():
            self.assertTrue({"title", "best", "average", "worst", "space"} <= set(entry))

    def test_index_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"canvas", res.data)

    def test_unknown_api_route_returns_json(self):
        res = self.client.get("/api/nope")
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())


class TestPseudocodeLines(ApiTestCase):
    """Every step's `line` must point at a real pseudocode line."""

    def test_lines_in_range(self):
        rng = random.Random(2)
        tree = None
        responses = []
        for v in rng.sample(range(100), 12):
            r = self.post("/api/bst/insert", {"tree": tree, "value": v})[1]
            tree = r["finalState"]
            responses.append(r)
        responses.append(self.post("/api/bst/search", {"tree": tree, "value": 7})[1])
        responses.append(self.post("/api/bst/delete", {"tree": tree, "value": tree["value"]})[1])
        for order in ("pre", "in", "post"):
            responses.append(self.post("/api/bst/traverse", {"tree": tree, "order": order})[1])
        g = {"vertices": list("ABCDE"), "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "E"], ["D", "E"]]}
        for algo in ("bfs", "dfs"):
            responses.append(self.post("/api/graph/" + algo, {"graph": g, "source": "A"})[1])
            responses.append(self.post("/api/graph/" + algo, {"graph": g, "source": "A", "destination": "E"})[1])
        h = {"array": []}
        for v in (9, 4, 7, 1, 3):
            r = self.post("/api/heap/insert", {"heap": h, "value": v})[1]
            h = r["finalState"]
            responses.append(r)
        while h["array"]:
            r = self.post("/api/heap/extract_min", {"heap": h})[1]
            h = r["finalState"]
            responses.append(r)
        responses.append(self.post("/api/stack/pop", {"stack": {"items": [1]}})[1])
        responses.append(self.post("/api/queue/dequeue", {"queue": {"items": [1]}})[1])
        for r in responses:
            for step in r["steps"]:
                self.assertLess(step["line"], len(r["pseudocode"]), (r["operation"], step["description"]))


if __name__ == "__main__":
    unittest.main()
