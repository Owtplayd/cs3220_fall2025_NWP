# lab4app_maze.py
# Lab 4: Random 2D Maze (0 wall, 1 open) + Uninformed Search (BFS/DFS)
# Node-based (draggable) PyVis view + Text grid view
# Start = yellow, Goal = green, Open = white, Walls = red

import sys, pathlib, tempfile
import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# Ensure project root on sys.path (so both root and src imports work)
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ----- core project imports (from src/) -----
from src.mazeData import (
    makeMaze,
    defineMazeAvailableActions,
    makeMazeTransformationModel,
    mazeStatesLocations,
)
from src.maze2025GraphClass import mazeGraph
from src.mazeProblemClass import MazeProblem
from src.mazeProblemSolvingAgentSMARTClass import MazeProblemSolvingAgentSMART

# tolerate uninformedSearchPrograms at src/ or root
try:
    from src.uninformedSearchPrograms import (
        BreadthFirstSearchAgentProgram,
        DepthFirstSearchAgentProgram,
    )
except ModuleNotFoundError:
    from uninformedSearchPrograms import (  # type: ignore
        BreadthFirstSearchAgentProgram,
        DepthFirstSearchAgentProgram,
    )


# ========================
# Session helpers
# ========================
def _init_state():
    ss = st.session_state
    ss.setdefault("n", 10)  # grid size
    ss.setdefault("seed", None)  # optional seed
    ss.setdefault("maze_arr", None)  # numpy 2D array
    ss.setdefault("state_space", None)  # {state: {action: next_state}}
    ss.setdefault("graph", None)  # mazeGraph over state_space
    ss.setdefault("start", (0, 0))
    ss.setdefault("goal", None)  # (n-1, n-1) after generation
    ss.setdefault("alg", "BFS")
    ss.setdefault("view", "Node Graph")  # "Node Graph" | "Text Grid"
    ss.setdefault("show_walls", True)  # show red wall nodes
    ss.setdefault("solution_nodes", [])
    ss.setdefault("solution_actions", [])
    ss.setdefault("step_idx", 0)
    ss.setdefault("log", [])


def narrate(msg: str):
    st.session_state["log"].append(msg)


# ========================
# Maze generation
# ========================
def generate_maze():
    ss = st.session_state

    if ss["seed"] not in (None, ""):
        try:
            np.random.seed(int(ss["seed"]))
        except Exception:
            narrate("Seed must be an integer; ignoring.")

    arr = np.array(makeMaze(ss["n"]), dtype=int)  # 0/1 grid
    acts = defineMazeAvailableActions(arr)  # legal actions per open cell
    state_space = makeMazeTransformationModel(acts)

    ss["maze_arr"] = arr
    ss["state_space"] = state_space
    ss["graph"] = mazeGraph(
        state_space, locations=mazeStatesLocations(list(state_space.keys()))
    )
    ss["goal"] = (ss["n"] - 1, ss["n"] - 1)
    ss["solution_nodes"] = []
    ss["solution_actions"] = []
    ss["step_idx"] = 0
    ss["log"] = []
    narrate(
        f"Generated {ss['n']}×{ss['n']} maze. Start={ss['start']}, Goal={ss['goal']}."
    )


def run_search():
    ss = st.session_state
    if ss["maze_arr"] is None:
        narrate("No maze yet. Click Generate.")
        return
    if ss["start"] not in ss["state_space"] or ss["goal"] not in ss["state_space"]:
        narrate("Start or Goal is a wall (0). Regenerate.")
        return

    problem = MazeProblem(initial=ss["start"], goal=ss["goal"], graph=ss["graph"])
    program = (
        BreadthFirstSearchAgentProgram()
        if ss["alg"] == "BFS"
        else DepthFirstSearchAgentProgram()
    )
    agent = MazeProblemSolvingAgentSMART(
        initial_state=ss["start"],
        dataGraph=ss["graph"],
        goal=ss["goal"],
        program=program,
    )
    goal_node = agent.program(problem)
    if goal_node is None:
        ss["solution_nodes"], ss["solution_actions"] = [], []
        narrate("No solution found.")
        return

    path_nodes = [n.state for n in goal_node.path()]
    ss["solution_nodes"] = path_nodes

    # derive action labels along the path from state_space
    actions = []
    for a, b in zip(path_nodes[:-1], path_nodes[1:]):
        for act, dest in ss["state_space"].get(a, {}).items():
            if dest == b:
                actions.append(act)
                break
        else:
            actions.append("?")
    ss["solution_actions"] = actions
    ss["step_idx"] = 0
    narrate(f"{ss['alg']} found a path with {len(path_nodes)-1} moves.")


def reset_app():
    st.session_state.clear()
    _init_state()
    narrate("Reset.")


# ========================
# Views / Rendering
# ========================
def draw_text_grid(arr: np.ndarray, path_states):
    """Minimal text grid."""
    n = arr.shape[0]
    path_set = set(path_states)
    lines = []
    for i in range(n):
        row = []
        for j in range(n):
            cell = (i, j)
            if cell == st.session_state["start"]:
                ch = "S "
            elif cell == st.session_state["goal"]:
                ch = "G "
            elif arr[i, j] == 0:
                ch = "█ "
            else:
                ch = "* " if cell in path_set else "· "
            row.append(ch)
        lines.append("".join(row))
    st.text("\n".join(lines))


def render_pyvis_maze(
    arr: np.ndarray, state_space: dict, path_states: list, show_walls: bool
):
    """
    Build a draggable node graph with PyVis:
      - open cells (1) -> white nodes (edges among them)
      - optional walls (0) -> red nodes (no edges)
      - start -> yellow, goal -> green
      - edges labeled by action, path edges highlighted green
    """
    from pyvis.network import Network

    n = arr.shape[0]
    net = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#1e1e1e",
        font_color="white",
    )
    net.barnes_hut()

    # VALID JSON for options
    net.set_options(
        """
    {
      "interaction": { "dragNodes": true, "hover": true, "multiselect": true },
      "physics": { "stabilization": { "iterations": 50 } },
      "edges": { "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } } }
    }
    """
    )

    def pos_for(i, j, spacing=60):
        return j * spacing, i * spacing

    path_set = set(path_states)

    # Add nodes
    for i in range(n):
        for j in range(n):
            cell = (i, j)
            x, y = pos_for(i, j)

            if arr[i, j] == 0:
                if not show_walls:
                    continue
                color = "#d33131"  # wall -> red
                label = ""  # keep compact
                title = f"Wall {cell}"
            else:
                if cell == st.session_state["start"]:
                    color, label = "#ffd43b", "S"  # start yellow
                elif cell == st.session_state["goal"]:
                    color, label = "#2ecc71", "G"  # goal green
                else:
                    color, label = "#ffffff", ("*" if cell in path_set else "")
                title = f"Open {cell}"

            # physics:true lets them drag; x/y give an initial layout
            net.add_node(
                str(cell),
                label=label,
                x=x,
                y=y,
                color=color,
                physics=True,
                title=title,
                shape="dot",
            )

    # Add edges for open cells only, labeled with action; highlight path edges
    path_edges = {(a, b) for a, b in zip(path_states[:-1], path_states[1:])}
    for a, act_map in state_space.items():
        for act, b in act_map.items():
            is_path = (a, b) in path_edges
            color = "#2ecc71" if is_path else "#cccccc"
            width = 4 if is_path else 1
            net.add_edge(str(a), str(b), label=act, color=color, width=width)

    # Write to temp HTML and embed (do NOT call net.show)
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
        net.write_html(f.name)
        html = pathlib.Path(f.name).read_text(encoding="utf-8")
    components.html(html, height=700, scrolling=True)


# ========================
# App entry
# ========================
def main():
    st.set_page_config(page_title="Lab 4: Maze (Uninformed Search)", layout="wide")
    _init_state()

    with st.sidebar:
        st.header("Maze Controls")
        st.number_input("Grid size (n×n)", 5, 50, key="n")
        st.text_input("Optional random seed", key="seed")
        st.selectbox("Algorithm", ["BFS", "DFS"], key="alg")
        st.selectbox("View", ["Node Graph", "Text Grid"], key="view")
        st.checkbox(
            "Show wall nodes (red)",
            key="show_walls",
            value=st.session_state["show_walls"],
        )

        if st.button("Generate / Regenerate"):
            generate_maze()
        if st.button("Run Search"):
            run_search()
        if st.button("Step Through Path"):
            if st.session_state["solution_nodes"]:
                ss = st.session_state
                ss["step_idx"] = min(ss["step_idx"] + 1, len(ss["solution_nodes"]) - 1)
                narrate(
                    f"Step {ss['step_idx']} at {ss['solution_nodes'][ss['step_idx']]}."
                )
            else:
                narrate("No solution yet. Click Run Search.")
        if st.button("Reset"):
            reset_app()

    st.title("Random 2D Maze + Uninformed Search (BFS/DFS)")
    st.caption(
        "Legend: **S** (yellow) Start • **G** (green) Goal • **white** open • **red** wall • **green edges** are the found path"
    )

    arr = st.session_state["maze_arr"]
    if arr is None:
        st.info("Click **Generate / Regenerate** to create a maze.")
        return

    step = st.session_state["step_idx"]
    path_states = (
        st.session_state["solution_nodes"][: step + 1]
        if st.session_state["solution_nodes"]
        else []
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Maze View")
        if st.session_state["view"] == "Node Graph":
            render_pyvis_maze(
                arr,
                st.session_state["state_space"],
                path_states,
                st.session_state["show_walls"],
            )
        else:
            draw_text_grid(arr, path_states)
            if st.session_state["solution_actions"]:
                shown = st.session_state["solution_actions"][:step]
                if shown:
                    st.write("Actions: " + " → ".join(shown))
    with c2:
        st.subheader("Narration Log")
        for i, line in enumerate(st.session_state["log"], 1):
            st.write(f"{i}. {line}")


if __name__ == "__main__":
    main()
