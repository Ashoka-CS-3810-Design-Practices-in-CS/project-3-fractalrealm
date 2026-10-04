

def dfs(graph, source, destination, log):
    state = graph.to_dict()
    adjacency = {v: graph.neighbors(v) for v in graph.vertices()}
    parent = {source: None}
    visited = [source]                       # discovery order == traversal order
    stack = [source]
    next_index = {source: 0}

    def aux():
        return {"stack": list(stack)}

    log.add("push", "Push the source %s and mark it visited" % source,
            state, line=0, current=[source], visited=visited, aux=aux())

    def finish_found():
        path = list(stack)                   # the stack is exactly the current path
        edges = [[path[i], path[i + 1]] for i in range(len(path) - 1)]
        log.add("found", "Destination %s reached. The stack holds the path: %s (not necessarily the shortest)"
                % (destination, " → ".join(path)),
                state, line=9, current=[destination], visited=visited, edges=edges, aux=aux())
        log.result = {"order": list(visited), "found": True, "path": path}
        return log

    if destination is not None and destination == source:
        return finish_found()

    while stack:
        v = stack[-1]
        i = next_index[v]
        if i < len(adjacency[v]):
            next_index[v] = i + 1
            w = adjacency[v][i]
            log.add("explore", "Explore edge (%s, %s) from the top of the stack" % (v, w),
                    state, line=3, current=[v], compared=[w], visited=visited,
                    edges=[[v, w]], aux=aux())
            if w not in parent:
                parent[w] = v
                visited.append(w)
                stack.append(w)
                next_index[w] = 0
                log.add("push", "%s is unvisited: mark it visited, set parent to %s and push it" % (w, v),
                        state, line=6, current=[w], visited=visited, edges=[[v, w]], aux=aux())
                if destination is not None and w == destination:
                    return finish_found()
        else:
            stack.pop()
            log.add("pop", "%s has no neighbours left: pop it and backtrack" % v,
                    state, line=8, current=[stack[-1]] if stack else [], visited=visited, aux=aux())

    if destination is not None:
        log.add("notFound", "The stack is empty: %s is not reachable from %s" % (destination, source),
                state, line=9, visited=visited, aux=aux())
        log.result = {"order": list(visited), "found": False, "path": None}
    else:
        log.add("visit", "The stack is empty: traversal complete. Order: %s" % " → ".join(visited),
                state, line=9, visited=visited, aux=aux())
        log.result = {"order": list(visited)}
    return log
