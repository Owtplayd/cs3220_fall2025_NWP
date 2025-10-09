# data/TreasureMazeData.py
# Defines a small undirected maze graph and its entrance/exit labels.


def undirected(d):
    # Ensure symmetry: for every a->b add b->a with same cost
    out = {}
    for a, nbrs in d.items():
        out.setdefault(a, {})
        for b, w in nbrs.items():
            out[a][b] = w
            out.setdefault(b, {})
            out[b][a] = w
    return out


# Nodes: S (start/entrance), E (exit), and internal junctions/corridors.
# We only include real “decision points” and endpoints (start, exit, dead-ends),
# exactly like the assignment asks.
_raw = {
    "S": {"A1": 1},  # Entrance
    "A1": {"A2": 1, "B1": 1},
    "A2": {"A3": 1},
    "A3": {"A4": 1, "C1": 1},
    "A4": {"B2": 1},  # a corridor bend
    "B1": {"B2": 1, "C1": 1},  # junction
    "B2": {"C2": 1},
    "C1": {"C2": 1, "D1": 1},  # junction
    "C2": {"D2": 1, "E": 1},  # near exit
    "D1": {"D2": 1},  # dead-end arm
    "D2": {"E": 1},  # corridor to exit
    "E": {},  # Exit
}

mazeData = undirected(_raw)
MAZE_START = "S"
MAZE_EXIT = "E"
