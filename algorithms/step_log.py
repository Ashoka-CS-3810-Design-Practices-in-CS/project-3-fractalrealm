"""StepLog: 

    {
      "stepIndex": int,
      "structureType": "bst" | "graph" | "heap" | "stack" | "queue",
      "action": one of VALID_ACTIONS,
      "description": str,            # shown under the canvas
      "line": int,                   # pseudocode line to highlight
      "highlight": {"current": [...], "visited": [...], "compared": [...], "edges": [[a, b], ...]},
      "aux": {"queue": [...]} or {"stack": [...]} or {},
      "structureState": {...},       # full snapshot AFTER this step
      "counters": {"comparisons": int, "operations": int}
    }
"""

VALID_STRUCTURES = ("bst", "graph", "heap", "stack", "queue")

VALID_ACTIONS = (
    "compare", "swap", "visit", "discover", "explore",
    "enqueue", "dequeue", "push", "pop",
    "insertNode", "removeNode", "found", "notFound",
)


class StepLog:
    def __init__(self, structure_type):
        if structure_type not in VALID_STRUCTURES:
            raise ValueError("Unknown structure type: %r" % (structure_type,))
        self.structure_type = structure_type
        self.steps = []
        self.comparisons = 0
        self.operations = 0
        # Algorithms store their final answer here (found?, path, order, ...).
        self.result = {}

    def add(self, action, description, state, line=0, current=None, visited=None,
            compared=None, edges=None, aux=None):
        """Append one step and return it."""
        if action not in VALID_ACTIONS:
            raise ValueError("Unknown step action: %r" % (action,))
        if action == "compare":
            self.comparisons += 1
        self.operations += 1
        step = {
            "stepIndex": len(self.steps),
            "structureType": self.structure_type,
            "action": action,
            "description": description,
            "line": line,
            "highlight": {
                "current": list(current or []),
                "visited": list(visited or []),
                "compared": list(compared or []),
                "edges": [list(e) for e in (edges or [])],
            },
            "aux": dict(aux) if aux else {},
            "structureState": state,
            "counters": {"comparisons": self.comparisons, "operations": self.operations},
        }
        self.steps.append(step)
        return step

    def __len__(self):
        return len(self.steps)
