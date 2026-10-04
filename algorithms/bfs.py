
from collections import deque


def _path_to(parent, target):
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return path[::-1]


def bfs(graph, source, destination, log):
    state = graph.to_dict()
    parent = {source: None}
    visited = [source]                       # discovery order == traversal order
    queue = deque([source])

    def aux():
        return {"queue": list(queue)}

    log.add("enqueue", "Enqueue the source %s and mark it visited" % source,
            state, line=0, visited=visited, aux=aux())

    def finish_found(dest):
        path = _path_to(parent, dest)
        edges = [[path[i], path[i + 1]] for i in range(len(path) - 1)]
        log.add("found", "Destination %s reached. Shortest path: %s (%d edge(s))"
                % (dest, " → ".join(path), len(path) - 1),
                state, line=8, current=[dest], visited=visited, edges=edges, aux=aux())
        log.result = {"order": list(visited), "found": True, "path": path, "distance": len(path) - 1}
        return log

    if destination is not None and destination == source:
        return finish_found(source)

    while queue:
        v = queue.popleft()
        log.add("dequeue", "Dequeue %s: it becomes the current vertex" % v,
                state, line=2, current=[v], visited=visited, aux=aux())
        for w in graph.neighbors(v):
            log.add("explore", "Explore edge (%s, %s)" % (v, w),
                    state, line=4, current=[v], compared=[w], visited=visited,
                    edges=[[v, w]], aux=aux())
            if w not in parent:
                parent[w] = v
                visited.append(w)
                queue.append(w)
                log.add("discover", "%s is unvisited: mark it visited, set parent to %s and enqueue it" % (w, v),
                        state, line=6, current=[v], visited=visited, edges=[[v, w]], aux=aux())
                if destination is not None and w == destination:
                    return finish_found(w)

    if destination is not None:
        log.add("notFound", "The queue is empty: %s is not reachable from %s" % (destination, source),
                state, line=8, visited=visited, aux=aux())
        log.result = {"order": list(visited), "found": False, "path": None}
    else:
        log.add("visit", "The queue is empty: traversal complete. Order: %s" % " → ".join(visited),
                state, line=8, visited=visited, aux=aux())
        log.result = {"order": list(visited)}
    return log
