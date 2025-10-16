# lab4app_asteroids.py
# Asteroid Maze & Satellites (UCS + IDS) with Node Graph view (draggable)

import sys, pathlib, tempfile
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# Ensure project root on path
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.asteroidData import (
    generate_asteroid_grid,
    place_enemies,
    start_goal,
    define_actions,
    make_transition_model,
    initial_performance,
    ACTION_COST,
    ACTION_NAMES,
    LEFT,
    UP,
    RIGHT,
    DOWN,
)
from src.asteroidProblemClass import AsteroidProblem
from src.uninformedSearchPrograms import (
    UniformCostSearchAgentProgram,
    IDSearchAgentProgram,
)


# --------------------------
# Session state
# --------------------------
def init_state():
    ss = st.session_state
    ss.setdefault("seed", "")
    ss.setdefault("n", 7)
    ss.setdefault("grid", None)
    ss.setdefault("enemies", None)  # {coord: power}
    ss.setdefault("S", None)
    ss.setdefault("G", None)
    ss.setdefault("origin", None)  # {state: {action: next_state}}
    ss.setdefault("uc_path", [])
    ss.setdefault("ids_path", [])
    ss.setdefault("uc_perf", 0)
    ss.setdefault("ids_perf", 0)
    ss.setdefault("log", [])
    ss.setdefault("view", "Node Graph")  # "Node Graph" | "Text Grid"
    ss.setdefault("show_walls", True)  # show asteroid nodes
    ss.setdefault("highlight", ["UCS"])  # which paths to draw: UCS / IDS


def log(msg):
    st.session_state["log"].append(msg)


# --------------------------
# Generation
# --------------------------
def generate():
    ss = st.session_state
    seed = None
    if ss["seed"] not in (None, ""):
        try:
            seed = int(ss["seed"])
        except Exception:
            log("Seed must be an integer; ignoring.")

    grid = generate_asteroid_grid(n=ss["n"], asteroid_ratio=0.25, seed=seed)
    enemies = place_enemies(grid, enemy_ratio=0.10, seed=seed)
    S, G = start_goal(grid)
    acts = define_actions(grid)
    origin = make_transition_model(acts)

    ss["grid"] = grid
    ss["enemies"] = enemies
    ss["S"], ss["G"] = S, G
    ss["origin"] = origin
    ss["uc_path"], ss["ids_path"] = [], []
    ss["uc_perf"] = ss["ids_perf"] = 0
    ss["log"] = []

    log(f"Generated {ss['n']}×{ss['n']} asteroid grid. S={S}, G={G}.")
    log(
        f"Free nodes: {int((grid==1).sum())}, Asteroids: {int((grid==0).sum())}, Enemies: {len(enemies)}."
    )


# --------------------------
# Search runners (planning phase)
# --------------------------
def run_uniform_cost():
    ss = st.session_state
    if ss["grid"] is None:
        log("Generate the environment first.")
        return
    problem = AsteroidProblem(initial=ss["S"], goal=ss["G"], origin=ss["origin"])
    program = UniformCostSearchAgentProgram()
    goal = program(problem)
    if goal is None:
        ss["uc_path"] = []
        log("Uniform-Cost: No route to goal.")
        return
    ss["uc_path"] = [n.state for n in goal.path()]
    log(
        f"Uniform-Cost: planned path with total cost {goal.path_cost} and {len(ss['uc_path'])-1} moves."
    )


def run_ids():
    ss = st.session_state
    if ss["grid"] is None:
        log("Generate the environment first.")
        return
    problem = AsteroidProblem(initial=ss["S"], goal=ss["G"], origin=ss["origin"])
    program = IDSearchAgentProgram(max_depth=ss["n"] * ss["n"])
    goal = program(problem)
    if goal is None:
        ss["ids_path"] = []
        log("IDS: No route to goal within limit.")
        return
    ss["ids_path"] = [n.state for n in goal.path()]
    log(
        f"IDS: planned path with {len(ss['ids_path'])-1} moves (cost computed on execution)."
    )


# --------------------------
# Execution phase (performance rules applied)
# --------------------------
def step_through(path, label: str):
    """
    Execute a path cell-by-cell applying:
    - Encounter enemy: if enemy_power >= 2 * current_perf -> captured (fail);
      else activate defense: perf -= 10% of current perf (>=1), continue.
    Returns final_perf, reached_goal(bool), events(list[str])
    """
    ss = st.session_state
    if not path:
        return 0, False, [f"{label}: no path to execute."]

    perf = initial_performance(ss["grid"])
    events = [f"{label}: start perf={perf} (50% of free nodes)."]
    enemies = dict(ss["enemies"])
    total_cost = 0

    for a, b in zip(path[:-1], path[1:]):
        move = _infer_action(a, b)
        total_cost += ACTION_COST[move]

        if b in enemies:
            power = enemies[b]
            if power >= 2 * perf:
                events.append(
                    f"{label}: ENCOUNTER at {b} (power {power}) >= 2×perf {perf} → CAPTURED."
                )
                return 0, False, events
            delta = max(1, int(np.floor(0.10 * perf)))
            perf = max(0, perf - delta)
            events.append(
                f"{label}: ENCOUNTER at {b} (power {power}); defense mode → -{delta} perf ⇒ {perf}."
            )

        if b == ss["G"]:
            events.append(
                f"{label}: reached GOAL with perf={perf}. Total path-cost={total_cost}."
            )
            return perf, True, events

    events.append(
        f"{label}: path ended without reaching goal. perf={perf}. Total path-cost={total_cost}."
    )
    return perf, False, events


def _infer_action(a, b):
    (i, j), (i2, j2) = a, b
    di, dj = i2 - i, j2 - j
    if (di, dj) == (0, -1):
        return LEFT
    elif (di, dj) == (-1, 0):
        return UP
    elif (di, dj) == (0, 1):
        return RIGHT
    elif (di, dj) == (1, 0):
        return DOWN
    raise ValueError(f"Non-adjacent move from {a} to {b}")


# --------------------------
# Rendering
# --------------------------
def draw_text_grid(grid: np.ndarray, enemies, S, G, path=None):
    n = grid.shape[0]
    path_set = set(path or [])
    lines = []
    for i in range(n):
        row = []
        for j in range(n):
            cell = (i, j)
            if cell == S:
                ch = "S "
            elif cell == G:
                ch = "G "
            elif grid[i, j] == 0:
                ch = "🪨 "
            elif cell in enemies:
                ch = "E "
            else:
                ch = "* " if cell in path_set else "· "
            row.append(ch)
        lines.append("".join(row))
    st.text("\n".join(lines))


def render_pyvis_asteroids(
    grid, enemies, S, G, origin, uc_path, ids_path, show_walls=True, highlight=("UCS",)
):
    from pyvis.network import Network

    n = grid.shape[0]
    net = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#1e1e1e",
        font_color="white",
    )
    net.barnes_hut()
    net.set_options(
        """
    {
      "interaction": { "dragNodes": true, "hover": true, "multiselect": true },
      "physics": { "stabilization": { "iterations": 50 } },
      "edges": { "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } } }
    }
    """
    )

    def pos_for(i, j, spacing=70):
        return j * spacing, i * spacing

    # Nodes
    uc_set = set(uc_path or [])
    ids_set = set(ids_path or [])
    for i in range(n):
        for j in range(n):
            cell = (i, j)
            x, y = pos_for(i, j)

            if grid[i, j] == 0:
                if not show_walls:
                    continue
                color = "rgba(180,180,180,0.35)"  # asteroids faint gray
                label = ""
                title = f"Asteroid {cell}"
                net.add_node(
                    str(cell),
                    label=label,
                    x=x,
                    y=y,
                    color=color,
                    size=8,
                    physics=False,
                    fixed=True,
                    title=title,
                    shape="dot",
                )
            else:
                # free cells
                if cell == S:
                    color, label = "#ffd43b", "S"  # start yellow
                elif cell == G:
                    color, label = "#2ecc71", "G"  # goal green
                elif cell in enemies:
                    color, label = "#ff6b6b", "E"  # enemy red-ish
                else:
                    # subtle highlight if on planned paths
                    if cell in uc_set and "UCS" in highlight:
                        color = "#b3ffd6"  # mint tint for UCS path nodes
                    elif cell in ids_set and "IDS" in highlight:
                        color = "#b3d1ff"  # light blue tint for IDS path nodes
                    else:
                        color = "#ffffff"
                    label = ""
                title = f"{'ENEMY ' if cell in enemies else ''}{cell}" + (
                    f" power={enemies[cell]}" if cell in enemies else ""
                )
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

    # Edges among free cells
    uc_edges = {(a, b) for a, b in zip(uc_path[:-1], uc_path[1:])} if uc_path else set()
    ids_edges = (
        {(a, b) for a, b in zip(ids_path[:-1], ids_path[1:])} if ids_path else set()
    )
    for a, act_map in origin.items():
        for act, b in act_map.items():
            color = "#7f8c8d"  # default gray
            width = 1
            if (a, b) in uc_edges and "UCS" in highlight:
                color, width = "#2ecc71", 4  # UCS edges green
            if (a, b) in ids_edges and "IDS" in highlight:
                # if both, blend by using blue with thicker width
                color, width = "#3498db", max(width, 4)
            net.add_edge(
                str(a), str(b), label=ACTION_NAMES[act], color=color, width=width
            )

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
        net.write_html(f.name)
        html = pathlib.Path(f.name).read_text(encoding="utf-8")
    components.html(html, height=700, scrolling=True)


# --------------------------
# App
# --------------------------
def main():
    st.set_page_config(
        page_title="Asteroid Maze & Satellites (UCS + IDS)", layout="wide"
    )
    init_state()

    with st.sidebar:
        st.header("Asteroid Controls")
        st.number_input("Grid size (n×n)", 5, 20, key="n")
        st.text_input("Optional Integer Seed", key="seed")
        st.selectbox("View", ["Node Graph", "Text Grid"], key="view")
        st.checkbox(
            "Show asteroid nodes (gray)",
            key="show_walls",
            value=st.session_state["show_walls"],
        )
        st.multiselect(
            "Highlight paths",
            ["UCS", "IDS"],
            default=st.session_state["highlight"],
            key="highlight",
        )

        if st.button("Generate / Regenerate"):
            generate()
        if st.button("Plan (Uniform-Cost)"):
            run_uniform_cost()
        if st.button("Plan (IDS)"):
            run_ids()
        if st.button("Run Both & Pick Winner"):
            run_both_and_pick_winner()

    st.title("Asteroid Maze & Satellites (UCS + IDS)")
    grid = st.session_state["grid"]
    if grid is None:
        st.info("Click **Generate / Regenerate** to create a 7×7 asteroid field.")
        return

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Environment")
        if st.session_state["view"] == "Text Grid":
            # show the longer of the two paths in text if present
            show_path = st.session_state["uc_path"] or st.session_state["ids_path"]
            draw_grid = draw_text_grid
            draw_grid(
                grid,
                st.session_state["enemies"],
                st.session_state["S"],
                st.session_state["G"],
                show_path,
            )
            st.caption("Legend: 🪨 asteroid • E enemy • S start • G goal • · free")
        else:
            render_pyvis_asteroids(
                grid,
                st.session_state["enemies"],
                st.session_state["S"],
                st.session_state["G"],
                st.session_state["origin"],
                st.session_state["uc_path"],
                st.session_state["ids_path"],
                show_walls=st.session_state["show_walls"],
                highlight=tuple(st.session_state["highlight"]),
            )

        # quick stats
        if st.session_state["uc_path"]:
            st.write(f"UCS planned length: {len(st.session_state['uc_path'])-1}")
        if st.session_state["ids_path"]:
            st.write(f"IDS planned length: {len(st.session_state['ids_path'])-1}")

    with c2:
        st.subheader("Narration Log")
        for i, line in enumerate(st.session_state["log"], 1):
            st.write(f"{i}. {line}")


def run_both_and_pick_winner():
    ss = st.session_state
    if ss["grid"] is None:
        log("Generate the environment first.")
        return
    if not ss["uc_path"]:
        run_uniform_cost()
    if not ss["ids_path"]:
        run_ids()

    # Execute (apply performance rules)
    uc_perf, uc_goal, uc_events = step_through(ss["uc_path"], "UCS")
    ids_perf, ids_goal, ids_events = step_through(ss["ids_path"], "IDS")

    ss["uc_perf"] = uc_perf
    ss["ids_perf"] = ids_perf

    for e in uc_events + ids_events:
        log(e)

    # Decide winner
    if uc_goal and ids_goal:
        if uc_perf > ids_perf:
            log(f"WINNER: UCS (perf {uc_perf} > {ids_perf}).")
        elif ids_perf > uc_perf:
            log(f"WINNER: IDS (perf {ids_perf} > {uc_perf}).")
        else:
            log(f"DRAW: both reached goal with equal perf {uc_perf}.")
    elif uc_goal and not ids_goal:
        log(f"WINNER: UCS (reached goal; IDS did not).")
    elif ids_goal and not uc_goal:
        log(f"WINNER: IDS (reached goal; UCS did not).")
    else:
        log("No winner: neither agent reached the goal.")


if __name__ == "__main__":
    main()
