# Interactive Data Structure and Algorithms Visualizer

A Flask + HTML canvas web app that animates BST, graph (BFS/DFS), min-heap priority queue, stack and queue
operations step by step, with complexity, pseudocode, undo/redo, test-case generation and a quiz.

## Run in VS Code

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate        macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

## Run the tests

```bash
python -m unittest discover -s tests -t . -v
```

(VS Code's Testing panel is pre-configured for unittest in `.vscode/settings.json`.)

## Architecture

| Layer | Folder | Role |
|---|---|---|
| Input/Output | `routes/`, `templates/`, `static/` | Flask routes, HTML, canvas drawing, playback, quiz |
| Application / Service | `services/` | Validation, rebuild structure from JSON, call algorithm, attach complexity + pseudocode |
| Algorithm | `algorithms/` | BST ops, traversals, BFS, DFS, heap ops, stack/queue ops; every one records a `StepLog` |
| Data Model | `models/` | BST, Graph (networkx), PriorityQueue, Stack, Queue |

The server is stateless: the browser holds the current structure and sends it with each request.
Undo/redo, the animation frame buffer and the history stack live in `static/js/`.

## API

All operations are `POST` with a JSON body and return
`{operation, steps, finalState, complexity, pseudocode, result}`; errors return `{"error": "..."}` with HTTP 400.

- `/api/bst/{insert,delete,search,traverse}`
- `/api/graph/{add_vertex,remove_vertex,add_edge,remove_edge,bfs,dfs,compare}`
- `/api/heap/{insert,extract_min,peek}`
- `/api/stack/{push,pop,peek,is_empty}`
- `/api/queue/{enqueue,dequeue,front,rear,is_empty}`
- `/api/generate`, `GET /api/reference`

## Limits

At most 25 nodes/vertices and 150 edges; integer values between -999 and 999.

## Documentation and demontration
https://drive.google.com/drive/folders/12Ne5yWxdYZa572Qp-G2t5TMdY7k7Co29?usp=sharing
