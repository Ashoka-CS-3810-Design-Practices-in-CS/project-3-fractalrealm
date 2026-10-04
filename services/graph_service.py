
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.step_log import StepLog
from errors import InvalidInputError, NotFoundError
from models.graph import Graph, normalize_label
from services.common import build_response, single_step_response


def _load(payload):
    return Graph.from_dict(payload.get("graph"))


# ------------------------------------------------------------------ editing
def add_vertex(payload):
    graph = _load(payload)
    v = graph.add_vertex(payload.get("vertex"))
    return single_step_response("graph", "insertNode", "Add vertex %s" % v, graph.to_dict(),
                                "graph.add_vertex", current=[v], result={"added": v})


def remove_vertex(payload):
    graph = _load(payload)
    v = graph.remove_vertex(payload.get("vertex"))
    return single_step_response("graph", "removeNode", "Remove vertex %s and all its edges" % v,
                                graph.to_dict(), "graph.remove_vertex", result={"removed": v})


def add_edge(payload):
    graph = _load(payload)
    u, v = graph.add_edge(payload.get("u"), payload.get("v"))
    step = single_step_response("graph", "insertNode", "Add edge (%s, %s)" % (u, v), graph.to_dict(),
                                "graph.add_edge", current=[u, v], result={"added": [u, v]})
    step["steps"][0]["highlight"]["edges"] = [[u, v]]
    return step


def remove_edge(payload):
    graph = _load(payload)
    u, v = graph.remove_edge(payload.get("u"), payload.get("v"))
    return single_step_response("graph", "removeNode", "Remove edge (%s, %s)" % (u, v), graph.to_dict(),
                                "graph.remove_edge", current=[u, v], result={"removed": [u, v]})


# ------------------------------------------------------------------ traversal
def _validate_start(graph, payload):
    """ER4: check the structure, the source and the optional destination before running."""
    if graph.is_empty():
        raise InvalidInputError("The graph is empty. Add vertices before running an algorithm")
    raw_source = payload.get("source")
    if raw_source is None or str(raw_source).strip() == "":
        raise InvalidInputError("Choose a source vertex first")
    source = normalize_label(raw_source)
    if not graph.has_vertex(source):
        raise NotFoundError("Source vertex '%s' is not in the graph" % source)
    raw_dest = payload.get("destination")
    destination = None
    if raw_dest is not None and str(raw_dest).strip() != "":
        destination = normalize_label(raw_dest)
        if not graph.has_vertex(destination):
            raise NotFoundError("Destination vertex '%s' is not in the graph" % destination)
    return source, destination


def _run(algorithm, key, graph, source, destination):
    log = StepLog("graph")
    algorithm(graph, source, destination, log)
    return build_response(log, graph.to_dict(), key)


def run_bfs(payload):
    graph = _load(payload)
    source, destination = _validate_start(graph, payload)
    return _run(bfs, "graph.bfs", graph, source, destination)


def run_dfs(payload):
    graph = _load(payload)
    source, destination = _validate_start(graph, payload)
    return _run(dfs, "graph.dfs", graph, source, destination)


def compare(payload):
    """FR6: run BFS and DFS on the same graph and return both step logs."""
    graph = _load(payload)
    source, destination = _validate_start(graph, payload)
    return {
        "bfs": _run(bfs, "graph.bfs", graph, source, destination),
        "dfs": _run(dfs, "graph.dfs", graph, source, destination),
    }
