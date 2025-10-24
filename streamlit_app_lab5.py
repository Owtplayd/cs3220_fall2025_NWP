# streamlit_app_lab5.py
# ---------------------------------------------------------------------
# Lab 5 Streamlit UI (node visualizations with PyVis) without changing
# your existing files. Place this file at the repo root and run:
#   streamlit run streamlit_app_lab5.py
# ---------------------------------------------------------------------

from __future__ import annotations
import streamlit as st
from typing import Dict, List, Tuple, Set
import json

# Core project imports (existing files)
from src.mazeData import makeMaze, defineMazeAvailableActions, makeMazeTransformationModel, mazeStatesLocations
from src.maze2025GraphClass import mazeGraph
from src.mazeProblemClass import MazeProblem
from src.graphClass import Graph

# New helpers generated for this lab
from src.informed_search_ext import (
    astar_euclidean, astar_manhattan, ida_star,
    make_multigoal_heuristic, make_multigoal_heuristic_mst, manhattan
)
from src.multigoal_problem_ext import MultiGoalMazeProblem
from src.pacman_world_ext import PacmanEnvironment

from pyvis.network import Network
import streamlit.components.v1 as components

State = Tuple[int, int]

# --------------------------- UI Helpers --------------------------------

def build_maze_graph(n: int) -> Tuple[mazeGraph, List[State], Dict[State, Tuple[int,int]]]:
    """Create a random n x n maze and convert to your mazeGraph using existing utilities."""
    arr = makeMaze(n)
    acts = defineMazeAvailableActions(arr)                 # {(i,j): [action_str, ...]}
    trans = makeMazeTransformationModel(acts)              # {(i,j): {action_str: (i2,j2), ...}}
    keys = list(trans.keys())
    locs = mazeStatesLocations(keys)                       # (i,j) -> (x,y) scaled positions
    g = mazeGraph(graph_dict=trans, locations=locs)        # your class
    open_nodes = [k for k in keys]                         # all non-wall nodes already filtered by acts/trans
    return g, open_nodes, arr

def pyvis_graph_from_maze(g: mazeGraph, path1: List[State] = None, path2: List[State] = None,
                          foods: Set[State] = None, ghosts: List[State] = None,
                          start: State = None, goal: State = None) -> str:
    """Render a PyVis graph with node-based coloring only (as requested). Returns HTML."""
    net = Network(height="650px", width="100%", directed=False, notebook=False)
    # Add nodes
    for node in g.nodes():
        # Base style
        color = "#CCCCCC"
        size = 12
        title = f"{node}"
        if foods and node in foods:
            color = "#32CD32"  # green
            title += " | food"
        if ghosts and node in ghosts:
            color = "#FF4C4C"  # red
            title += " | ghost"
        if start and node == start:
            color = "#FFD700"  # gold
            size = 18
            title += " | START"
        if goal and node == goal:
            color = "#1E90FF"  # blue
            size = 18
            title += " | GOAL"

        # Path coloring overlays (node-based, not edges)
        if path1 and node in path1:
            color = "#8A2BE2"  # purple for Euclidean A*
            title += " | A*:Euclid"
        if path2 and node in path2:
            # If both paths use the node, mix indication in title
            if path1 and node in path1:
                title += " & A*:Manhattan"
                color = "#FF7F50"  # coral to differentiate overlap
            else:
                color = "#FFA500"  # orange for Manhattan

        net.add_node(str(node), label=str(node), color=color, size=size, title=title)

    # Add undirected edges from g.get(a) dict
    seen = set()
    for a in g.nodes():
        for b in g.get(a).keys():
            edge = tuple(sorted((str(a), str(b))))
            if edge in seen:
                continue
            seen.add(edge)
            net.add_edge(str(a), str(b))

    net.toggle_physics(False)  # keep grid-like layout
    return net.generate_html()

# --------------------------- Streamlit UI -------------------------------

st.set_page_config(page_title="Lab 5 — Informed Search", layout="wide")
st.title("Lab 5 — Informed Search (Pac‑Man World)")

with st.sidebar:
    st.header("Maze builder")
    n = st.slider("Maze size (n × n)", min_value=5, max_value=20, value=10, step=1)
    seed = st.number_input("Random seed (for foods/ghosts)", value=42, step=1)
    st.caption("Re-run to regenerate maze. Start=(0,0), Goal=(n-1,n-1).")

# Build maze graph and show
g, nodes_all, arr = build_maze_graph(n)
start = (0, 0)
goal = (n-1, n-1)

# --------------------- Tasks 1 & 2: A* variants ------------------------
st.subheader("Tasks 1 & 2 — A* (Euclidean vs Manhattan)")

problem = MazeProblem(start, goal, g)

states_e, actions_e, expanded_e, cost_e = astar_euclidean(problem)
states_m, actions_m, expanded_m, cost_m = astar_manhattan(problem)

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Euclidean A*** — cost = `{cost_e}` | nodes expanded = `{expanded_e}`")
with col2:
    st.write(f"**Manhattan A*** — cost = `{cost_m}` | nodes expanded = `{expanded_m}`")

html = pyvis_graph_from_maze(g, path1=states_e, path2=states_m, start=start, goal=goal)
components.html(html, height=680, scrolling=True)

# --------------------- Task 3: Foods & Ghosts --------------------------
st.subheader("Task 3 — Pac‑Man World (10% foods & 5 ghosts)")

env = PacmanEnvironment(g, start, goal, food_ratio=0.10, num_ghosts=5, seed=int(seed))

colf1, colf2 = st.columns(2)
with colf1:
    st.write(f"Foods placed: **{len(env.foods)}**")
with colf2:
    st.write(f"Ghosts placed: **{len(env.ghosts)}**")

ghost_positions = [gh.pos for gh in env.ghosts]
html_world = pyvis_graph_from_maze(
    g, path1=states_e, foods=env.foods, ghosts=ghost_positions, start=start, goal=goal
)
components.html(html_world, height=680, scrolling=True)

# --------------------- Task 4: Multi‑goal Heuristic --------------------
st.subheader("Task 4 — Multi‑goal Heuristic (collect foods, then finish)")

use_mst = st.checkbox("Use tighter MST lower bound", value=True)
foods_list = list(env.foods)

# Heuristic that reads full multi‑goal state (pos, remaining_foods)
def h_multigoal(state):
    pos, remain = state
    remain_list = list(remain)
    # nearest-food + optional MST over remaining foods (admissible)
    if remain_list:
        d0 = min(manhattan(pos, f) for f in remain_list)
        if use_mst and len(remain_list) > 1:
            # reuse informed_search_ext.mst_lower_bound to avoid code dup
            from src.informed_search_ext import mst_lower_bound
            return d0 + mst_lower_bound(remain_list)
        return d0
    return manhattan(pos, goal)

# --------------------- Task 6: IDA* on Multi‑goal ----------------------
st.subheader("Task 6 — IDA* on Multi‑goal Pac‑Man")

mg_problem = MultiGoalMazeProblem(start, goal, set(foods_list), g)
states_ida, actions_ida, expanded_ida, cost_ida = ida_star(mg_problem, h_multigoal)

st.write(f"**IDA\*** — cost = `{cost_ida}` | nodes expanded = `{expanded_ida}` | path length = `{len(states_ida)}`")

# Visualize: multi‑goal path nodes layered on top
html_mg = pyvis_graph_from_maze(
    g, path1=states_ida, foods=set(foods_list), ghosts=ghost_positions, start=start, goal=goal
)
components.html(html_mg, height=680, scrolling=True)

# ------------------------ Simulation (Task 5) --------------------------
st.subheader("Task 5 — Performance & Ghost Encounters (simulate A* path)")

chosen = st.selectbox("Choose a path to simulate", ["Euclidean A*", "Manhattan A*", "IDA* (multi‑goal)"])
if chosen == "Euclidean A*":
    sim_path = states_e
elif chosen == "Manhattan A*":
    sim_path = states_m
else:
    sim_path = states_ida

report = env.simulate_path(sim_path)

st.write("**Simulation report**")
st.json(report)
