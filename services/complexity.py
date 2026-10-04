


def _c(title, best, average, worst, space, note=""):
    return {"title": title, "best": best, "average": average, "worst": worst,
            "space": space, "note": note}


COMPLEXITY = {
    # ---- BST
    "bst.insert": _c("BST Insert", "O(1)", "O(log n)", "O(n)", "O(h)",
                     "Worst case when the tree is a chain (e.g. sorted input)."),
    "bst.delete": _c("BST Delete", "O(1)", "O(log n)", "O(n)", "O(h)",
                     "The two-child case also walks down to the in-order successor."),
    "bst.search": _c("BST Search", "O(1)", "O(log n)", "O(n)", "O(1)",
                     "Iterative loop down one path, so no extra stack is needed."),
    "bst.traverse": _c("BST Traversal (pre / in / post)", "O(n)", "O(n)", "O(n)", "O(h)",
                       "Every node is visited exactly once; h is the recursion depth."),
    # ---- Graph
    "graph.bfs": _c("Breadth-First Search", "O(V + E)", "O(V + E)", "O(V + E)", "O(V)",
                    "Uses a queue. Finds shortest paths in unweighted graphs."),
    "graph.dfs": _c("Depth-First Search", "O(V + E)", "O(V + E)", "O(V + E)", "O(V)",
                    "Uses a stack. The path found is not always the shortest."),
    "graph.add_vertex": _c("Add Vertex", "O(1)", "O(1)", "O(1)", "O(1)"),
    "graph.remove_vertex": _c("Remove Vertex", "O(1)", "O(deg(v))", "O(V)", "O(1)",
                              "Every edge touching the vertex is removed too."),
    "graph.add_edge": _c("Add Edge", "O(1)", "O(1)", "O(1)", "O(1)"),
    "graph.remove_edge": _c("Remove Edge", "O(1)", "O(1)", "O(1)", "O(1)"),
    # ---- Priority queue (min-heap)
    "heap.insert": _c("Heap Insert (sift-up)", "O(1)", "O(1)", "O(log n)", "O(1)",
                      "Only the path from the new leaf to the root can be out of order."),
    "heap.extract_min": _c("Heap Extract-Min (sift-down)", "O(1)", "O(log n)", "O(log n)", "O(1)"),
    "heap.peek": _c("Heap Peek", "O(1)", "O(1)", "O(1)", "O(1)"),
    # ---- Stack
    "stack.push": _c("Stack push()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "stack.pop": _c("Stack pop()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "stack.peek": _c("Stack peek()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "stack.is_empty": _c("Stack isEmpty()", "O(1)", "O(1)", "O(1)", "O(1)"),
    # ---- Queue
    "queue.enqueue": _c("Queue enqueue()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "queue.dequeue": _c("Queue dequeue()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "queue.front": _c("Queue front()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "queue.rear": _c("Queue rear()", "O(1)", "O(1)", "O(1)", "O(1)"),
    "queue.is_empty": _c("Queue isEmpty()", "O(1)", "O(1)", "O(1)", "O(1)"),
    # ---- Test-case generation (cost of building the structure)
    "generate.bst": _c("Generate BST (n inserts)", "O(n log n)", "O(n log n)", "O(n²)", "O(n)",
                       "Ascending / descending input makes the tree a chain."),
    "generate.heap": _c("Generate Heap (n inserts)", "O(n)", "O(n)", "O(n log n)", "O(n)"),
    "generate.stack": _c("Generate Stack (n pushes)", "O(n)", "O(n)", "O(n)", "O(n)"),
    "generate.queue": _c("Generate Queue (n enqueues)", "O(n)", "O(n)", "O(n)", "O(n)"),
    "generate.graph": _c("Generate Graph", "O(V + E)", "O(V + E)", "O(V + E)", "O(V + E)"),
}


def get_complexity(key):
    return dict(COMPLEXITY[key])
