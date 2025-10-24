# streamlit_app_lab5.py
# ---------------------------------------------------------------------
# Streamlit UI. Ensures project root on sys.path; uses heuristics only
# from src.informed_search_ext (no separate heuristics module).
# ---------------------------------------------------------------------

from __future__ import annotations

# --- ensure project root is on sys.path so 'src.*' imports work ---
import sys, pathlib

ROOT = pathlib.Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------------------------

import streamlit as st
from typing import Dict, List, Tuple, Set
from pyvis.network import Network
import streamlit.components.v1 as components

from src.mazeData import (
    makeMaze,
    defineMazeAvailableActions,
    makeMazeTransformationModel,
    mazeStatesLocations,
)
from src.maze2025GraphClass import mazeGraph
from src.mazeProblemClass import MazeProblem

from src.informed_search_ext import (
    astar_euclidean,
    astar_manhattan,
    ida_star,
    manhattan,
    mst_lower_bound,
)
from src.multigoal_problem_ext import MultiGoalMazeProblem
from src.pacman_world_ext import PacmanEnvironment

State = Tuple[int, int]


def build_maze_graph(n: int) -> Tuple[mazeGraph, List[State], List[List[int]]]:
    arr = makeMaze(n)
    acts = defineMazeAvailableActions(arr)
    trans = makeMazeTransformationModel(acts)
    keys = list(trans.keys())
    locs = mazeStatesLocations(keys)
    g = mazeGraph(graph_dict=trans, locations=locs)
    open_nodes = [k for k in keys]
    return g, open_nodes, arr


def pyvis_graph_from_maze(
    g: mazeGraph,
    path1: List[State] = None,
    path2: List[State] = None,
    foods: Set[State] = None,
    ghosts: List[State] = None,
    start: State = None,
    goal: State = None,
) -> str:
    net = Network(height="650px", width="100%", directed=False, notebook=False)
    for node in g.nodes():
        color = "#CCCCCC"
        size = 12
        title = f"{node}"
        if foods and node in foods:
            color = "#32CD32"
            title += " | food"
        if ghosts and node in ghosts:
            color = "#FF4C4C"
            title += " | ghost"
        if start and node == start:
            color = "#FFD700"
            size = 18
            title += " | START"
        if goal and node == goal:
            color = "#1E90FF"
            size = 18
            title += " | GOAL"
        if path1 and node in path1:
            color = "#8A2BE2"
            title += " | A*:Euclid"
        if path2 and node in path2:
            if path1 and node in path1:
                title += " & A*:Manhattan"
                color = "#FF7F50"
            else:
                color = "#FFA500"
        net.add_node(str(node), label=str(node), color=color, size=size, title=title)

    seen = set()
    for a in g.nodes():
        for b in g.get(a).keys():
            e = tuple(sorted((str(a), str(b))))
            if e in seen:
                continue
            seen.add(e)
            net.add_edge(str(a), str(b))

    net.toggle_physics(False)
    return net.generate_html()


st.set_page_config(page_title="Lab 5 — Informed Search", layout="wide")
st.title("Lab 5 — Informed Search (Pac-Man World)")

with st.sidebar:
    st.header("Maze builder")
    n = st.slider("Maze size (n × n)", min_value=5, max_value=20, value=10, step=1)
    seed = st.number_input("Random seed (for foods/ghosts)", value=42, step=1)
    st.caption("Re-run to regenerate maze. Start=(0,0), Goal=(n-1,n-1).")

g, nodes_all, arr = build_maze_graph(n)
start = (0, 0)
goal = (n - 1, n - 1)

st.subheader("Tasks 1 & 2 — A* (Euclidean vs Manhattan)")
problem = MazeProblem(start, goal, g)
states_e, actions_e, expanded_e, cost_e = astar_euclidean(problem)
states_m, actions_m, expanded_m, cost_m = astar_manhattan(problem)
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Euclidean A*** — cost = `{cost_e}` | nodes expanded = `{expanded_e}`")
with col2:
    st.write(f"**Manhattan A*** — cost = `{cost_m}` | nodes expanded = `{expanded_m}`")
components.html(
    pyvis_graph_from_maze(g, path1=states_e, path2=states_m, start=start, goal=goal),
    height=680,
    scrolling=True,
)

st.subheader("Task 3 — Pac-Man World (10% foods & 5 ghosts)")
env = PacmanEnvironment(g, start, goal, food_ratio=0.10, num_ghosts=5, seed=int(seed))
ghost_positions = [gh.pos for gh in env.ghosts]
colf1, colf2 = st.columns(2)
with colf1:
    st.write(f"Foods placed: **{len(env.foods)}**")
with colf2:
    st.write(f"Ghosts placed: **{len(env.ghosts)}**")
components.html(
    pyvis_graph_from_maze(
        g,
        path1=states_e,
        foods=env.foods,
        ghosts=ghost_positions,
        start=start,
        goal=goal,
    ),
    height=680,
    scrolling=True,
)

st.subheader("Task 4 — Multi-goal Heuristic (collect foods, then finish)")
use_mst = st.checkbox("Use tighter MST lower bound", value=True)
foods_list = list(env.foods)


def h_multigoal(state):
    pos, remain = state
    remain_list = list(remain)
    if remain_list:
        d0 = min(manhattan(pos, f) for f in remain_list)
        if use_mst and len(remain_list) > 1:
            return d0 + mst_lower_bound(remain_list)
        return d0
    return manhattan(pos, goal)


st.subheader("Task 6 — IDA* on Multi-goal Pac-Man")
from src.multigoal_problem_ext import MultiGoalMazeProblem

mg_problem = MultiGoalMazeProblem(start, goal, set(foods_list), g)
states_ida, actions_ida, expanded_ida, cost_ida = ida_star(mg_problem, h_multigoal)
st.write(
    f"**IDA*** — cost = `{cost_ida}` | nodes expanded = `{expanded_ida}` | path length = `{len(states_ida)}`"
)
components.html(
    pyvis_graph_from_maze(
        g,
        path1=states_ida,
        foods=set(foods_list),
        ghosts=ghost_positions,
        start=start,
        goal=goal,
    ),
    height=680,
    scrolling=True,
)

st.subheader("Task 5 — Performance & Ghost Encounters (simulate A* path)")
choice = st.selectbox(
    "Choose a path to simulate", ["Euclidean A*", "Manhattan A*", "IDA* (multi-goal)"]
)
sim_path = (
    states_e
    if choice == "Euclidean A*"
    else states_m if choice == "Manhattan A*" else states_ida
)
report = env.simulate_path(sim_path)
st.json(report)
