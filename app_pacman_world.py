# app_pacman_world.py
# Streamlit demo for Lab 5 Pac-Man World
# - A*: Euclidean vs Manhattan (prints nodes expanded + path cost)
# - Multi-goal plan: collect all food then reach the goal
# - Optional IDA*
#
# We DO NOT edit your src/ files. We only adapt imports and pass the right
# shape to MazeProblem (a TM-backed mapping it can index).

import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DATA = os.path.join(ROOT, "data")
for p in (SRC, DATA):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---- DATA knobs + world sampler (lowercase module name in your repo) ----
try:
    from data.pacmanWorldData import derive_world, USE_MANHATTAN, USE_IDASTAR
except ModuleNotFoundError:
    from data.pacmanWorldData import (
        derive_world,
        USE_MANHATTAN,
        USE_IDASTAR,
    )  # fallback if capitalized

# ---- Your original modules (imported unqualified so inner imports work) ----
from mazeData import (
    makeMaze,
    defineMazeAvailableActions,
    makeMazeTransformationModel,
    mazeStatesLocations,
)
from mazeGraphClass import mazeGraph  # used for viz only
from mazeProblemClass import MazeProblem
from mazeProblemSolvingAgentSMARTClass import MazeProblemSolvingAgentSMART

# ---- Small helpers added for this lab (kept in src/) ----
from PS_agentPrograms_extra import A_Star_Euclidean, A_Star_Manhattan, IDAStar
from pacman_multi_goal_agent import PacmanPlanner


# ---- Minimal problem-graph view for MazeProblem (dict-like, indexable) ----
class _ProblemGraphView:
    """
    Exactly what MazeProblem expects:
      - .origin is a dict: state -> {action: successor_state, ...}
      - .nodes() returns the set/list of states
    """

    def __init__(self, tm_dict):
        self.origin = tm_dict

    def nodes(self):
        return list(self.origin.keys())


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Pac-Man World (Lab 5)", layout="wide")
st.title("Lab 5 · Pac-Man World: A*, Manhattan vs Euclidean, IDA*")

# Sidebar
st.sidebar.header("Maze")
rows = st.sidebar.slider("Rows", 8, 30, 12, 1)
cols = st.sidebar.slider("Cols", 8, 30, 12, 1)

st.sidebar.header("Search")
use_manhattan = st.sidebar.checkbox("Use Manhattan heuristic", value=USE_MANHATTAN)
use_idastar = st.sidebar.checkbox("Use IDA* (instead of A*)", value=USE_IDASTAR)

# 1) Build 2D maze (0 wall, 1 open). Some repos use makeMaze(size); others makeMaze(rows, cols).
try:
    maze_matrix = makeMaze(rows, cols)
except TypeError:
    size = rows if rows == cols else min(rows, cols)
    if rows != cols:
        st.info(f"Your makeMaze(size) builds square mazes; using size={size}.")
    maze_matrix = makeMaze(size)
    rows, cols = size, size

start = (0, 0)
goal = (rows - 1, cols - 1)

# 2) === SNIPPET: enrich world with food & ghosts ===
world = derive_world(maze_matrix, start, goal)
foods = world["foods"]
ghosts = world["ghosts"]
open_cells = world["open_cells"]

# 3) Build state space & graph using your pipeline
ava = defineMazeAvailableActions(maze_matrix)
TM = makeMazeTransformationModel(ava)  # dict: state -> {action: successor}
locs = mazeStatesLocations(list(TM.keys()))
G_viz = mazeGraph(TM, locs)  # keep for visualization/planner

# >>> Provide MazeProblem a TM-backed view it can index <<<
G_for_problem = _ProblemGraphView(TM)

# 4) Single-goal A* showcases (Task 1 & 2)
col1, col2 = st.columns(2)
with col1:
    st.subheader("A* (Euclidean)")
    agent_e = MazeProblemSolvingAgentSMART(
        initial_state=start,
        dataGraph=G_for_problem,
        goal=goal,
        program=A_Star_Euclidean(),
    )
    prob_e = MazeProblem(start, goal, G_for_problem)
    _ = agent_e.search(prob_e)

with col2:
    st.subheader("A* (Manhattan)")
    agent_m = MazeProblemSolvingAgentSMART(
        initial_state=start,
        dataGraph=G_for_problem,
        goal=goal,
        program=A_Star_Manhattan(),
    )
    prob_m = MazeProblem(start, goal, G_for_problem)
    _ = agent_m.search(prob_m)

# 5) Multi-goal Pac-Man planner (Tasks 3–7)
st.subheader("Pac-Man: collect all Fixed Food Dots, then reach the goal")
planner = PacmanPlanner(
    graph=G_viz,  # planner can use your real graph class
    open_cells=open_cells,
    start=start,
    goal=goal,
    foods=set(foods),
    use_manhattan=use_manhattan,
    use_idastar=use_idastar,
)
report = planner.build_plan()

# 6) Visualization (maze grid + food + ghosts + colored segments)
arr = np.array(maze_matrix)
rows, cols = arr.shape
fig, ax = plt.subplots(figsize=(8, 8))

base = np.zeros_like(arr, dtype=float)
base[arr == 0] = 0.0
base[arr != 0] = 0.6
ax.imshow(base, cmap="binary", origin="upper")

# start/goal
ax.scatter([start[1]], [start[0]], s=200, marker="s", c="lime", label="start")
ax.scatter([goal[1]], [goal[0]], s=200, marker="s", c="red", label="goal")

# food
if foods:
    fy = [r for (r, c) in foods]
    fx = [c for (r, c) in foods]
    ax.scatter(fx, fy, s=60, c="gold", marker="o", label="food")

# ghosts
if ghosts:
    gy = [r for (r, c) in ghosts]
    gx = [c for (r, c) in ghosts]
    ax.scatter(gx, gy, s=80, c="crimson", marker="x", label="ghost")

# path segments (each leg its own color)
for seg in report["segments"]:
    path = seg["path"]
    xs = [c for (r, c) in path]
    ys = [r for (r, c) in path]
    ax.plot(xs, ys, linewidth=3, color=seg["color"])

ax.set_xticks(range(cols))
ax.set_yticks(range(rows))
ax.grid(color="gray", linewidth=0.5, alpha=0.3)
ax.set_xlim(-0.5, cols - 0.5)
ax.set_ylim(rows - 0.5, -0.5)
ax.legend(loc="upper right")
st.pyplot(fig)

# 7) Stats
st.markdown("### Stats")
st.write(
    {
        "heuristic": "Manhattan" if use_manhattan else "Euclidean",
        "search": "IDA*" if use_idastar else "A*",
        "total_nodes_expanded": report["nodes_expanded"],
        "total_path_cost": report["total_cost"],
        "final_performance_percent": round(report["final_performance_percent"], 2),
        "ghost_count": len(ghosts),
        "food_count": len(foods),
    }
)
