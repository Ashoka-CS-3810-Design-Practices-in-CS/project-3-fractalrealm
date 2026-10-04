import unittest

from algorithms.step_log import StepLog


class TestStepLog(unittest.TestCase):
    def test_step_schema(self):
        log = StepLog("bst")
        step = log.add("compare", "Compare 1 with 2", {"value": 2}, line=2, current=[2], visited=[1],
                       compared=[3], edges=[("a", "b")], aux={"queue": ["a"]})
        self.assertEqual(set(step), {"stepIndex", "structureType", "action", "description", "line",
                                     "highlight", "aux", "structureState", "counters"})
        self.assertEqual(set(step["highlight"]), {"current", "visited", "compared", "edges"})
        self.assertEqual(step["highlight"]["edges"], [["a", "b"]])
        self.assertEqual(step["stepIndex"], 0)

    def test_counters(self):
        log = StepLog("heap")
        log.add("compare", "c", {})
        log.add("swap", "s", {})
        log.add("compare", "c", {})
        self.assertEqual(log.steps[-1]["counters"], {"comparisons": 2, "operations": 3})
        self.assertEqual(len(log), 3)
        self.assertEqual([s["stepIndex"] for s in log.steps], [0, 1, 2])

    def test_rejects_unknown_action_or_structure(self):
        with self.assertRaises(ValueError):
            StepLog("bst").add("explode", "x", {})
        with self.assertRaises(ValueError):
            StepLog("tree")

    def test_highlight_lists_are_copies(self):
        log = StepLog("graph")
        visited = ["A"]
        log.add("visit", "v", {}, visited=visited)
        visited.append("B")
        self.assertEqual(log.steps[0]["highlight"]["visited"], ["A"])


if __name__ == "__main__":
    unittest.main()
