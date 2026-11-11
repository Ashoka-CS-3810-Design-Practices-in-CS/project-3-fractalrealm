"""Central configuration constants shared by every layer."""

# ER3: the display stays readable up to this many nodes / vertices.
MAX_NODES = 25

# A 50-vertex complete graph has 1225 edges and is unreadable (and every BFS/DFS
# step carries a full snapshot), so edges are capped as well.
MAX_EDGES = 150

# Integer values accepted by BST / heap / stack / queue (keeps labels short).
VALUE_MIN = -999
VALUE_MAX = 999

# Longest allowed vertex label.
MAX_LABEL_LENGTH = 8
