# lab3app_wgc.py
# Streamlit app to visualize & solve WGC using your Problem-Solving Agent
import streamlit as st
import streamlit.components.v1 as components

from src.wgcStateSpaceGraph import build_state_space_html
from src.wgcProblemClass import WGCProblem
from src.PS_agentPrograms import BestFirstSearchAgentProgram
from src.nodeClass import Node

st.set_page_config(page_title="Wolf–Goat–Cabbage Planner", layout="wide")
st.title("Wolf–Goat–Cabbage — Problem-Solving Agent")


def nodes_from_solution(sol):
    """
    Accepts:
      • a goal Node,
      • a list of Nodes (root..goal),
      • or anything with .solution() / .path().
    Returns: list[Node] from root to goal.
    """
    if isinstance(sol, Node):
        nodes = []
        cur = sol
        while cur is not None:
            nodes.append(cur)
            cur = getattr(cur, "parent", None)
        return list(reversed(nodes))

    if isinstance(sol, (list, tuple)) and len(sol) > 0 and isinstance(sol[0], Node):
        return list(sol)

    for attr in ("path", "solution"):
        if hasattr(sol, attr):
            maybe = getattr(sol, attr)
            maybe = maybe() if callable(maybe) else maybe
            if (
                isinstance(maybe, (list, tuple))
                and maybe
                and isinstance(maybe[0], Node)
            ):
                return list(maybe)
    return []


def side_arrow(src, dst):
    return f"{src}→{dst}"


def who_name(letter):
    return {"F": "Farmer", "W": "Wolf", "G": "Goat", "C": "Cabbage"}[letter]


def narrate(action, s_before, s_after):
    """
    Produce a friendly sentence describing the action and movement.
    States are (F, W, G, C) with 'L' or 'R'.
    Actions: 'F', 'FW', 'FG', 'FC'
    """
    f0, w0, g0, c0 = s_before
    f1, w1, g1, c1 = s_after
    # Farmer always moves; figure out direction:
    dir_txt = side_arrow(f0, f1)

    if action == "F":
        return f"Farmer rows alone {dir_txt}."
    elif action in ("FW", "FG", "FC"):
        carried = action[-1]  # 'W' or 'G' or 'C'
        # sanity: confirm item moved with farmer
        moved_ok = {"W": (w0, w1), "G": (g0, g1), "C": (c0, c1)}[carried][0] != {
            "W": (w0, w1),
            "G": (g0, g1),
            "C": (c0, c1),
        }[carried][1]
        # Name + direction:
        who = who_name(carried)
        # If something odd, still describe intent:
        return f"Farmer takes {who} {dir_txt}."
    else:
        return f"Action {action}: Farmer rows {dir_txt}."


def format_state(s):
    f, w, g, c = s
    return f"(F:{f}, W:{w}, G:{g}, C:{c})"


# ---------------- UI ----------------
col1, col2 = st.columns(2)

with col1:
    cost_mode = st.radio(
        "Cost version:",
        ["v1", "v1.01"],
        index=0,
        help="v1: each crossing costs 1. v1.01: boat(1) + handling: cabbage(+2), wolf/goat(+3).",
    )
    html_file = build_state_space_html(
        filename=f"graph_wgc_{cost_mode}.html", cost_mode=cost_mode
    )
    st.subheader("State Space (PyVis)")
    with open(html_file, "r", encoding="utf-8") as f:
        components.html(f.read(), height=750, scrolling=True)

with col2:
    st.subheader("Search (Best-First)")
    prob = WGCProblem(cost_mode=cost_mode)

    program = BestFirstSearchAgentProgram()
    try:
        sol = program(prob)
    except TypeError:
        solver_fn = program
        sol = solver_fn(prob)

    nodes = nodes_from_solution(sol)

    if nodes:
        actions = [n.action for n in nodes[1:]]
        total_cost = nodes[-1].path_cost

        st.write("**States along path (raw):**")
        for i, n in enumerate(nodes):
            act = f"  ← {n.action}" if i > 0 else ""
            st.write(f"Step {i}: {n.state}{act}   (g={n.path_cost})")

        st.success(f"Plan: {actions}")
        st.info(f"Total cost: {total_cost}")

        st.markdown("---")
        st.subheader("Narration")
        st.caption("Readable description of each move with state and incremental cost.")
        for i in range(1, len(nodes)):
            prev = nodes[i - 1]
            cur = nodes[i]
            a = cur.action
            inc = cur.path_cost - prev.path_cost
            sentence = narrate(a, prev.state, cur.state)
            st.write(
                f"**Move {i}:** {sentence}  "
                f"`{format_state(prev.state)} → {format_state(cur.state)}`  "
                f"(step cost: {inc}, g={cur.path_cost})"
            )
    else:
        st.warning(
            "Could not interpret the return shape from BestFirstSearchAgentProgram."
        )
        st.write("Raw object returned by program:", sol)

st.markdown("---")
with st.expander("What’s the difference between v1 and v1.01, and why have both?"):
    st.markdown(
        """
**Version v1 (uniform-cost):** every crossing costs 1.  
This treats all actions as equally expensive. It’s great for illustrating the basic
state space and finding a shortest plan in terms of *number of crossings*.

**Version v1.01 (weighted-cost):** cost = boat move (1) **+ handling**  
- Farmer alone: +0  → total 1  
- With Cabbage: +2 → total 3  
- With Wolf/Goat: +3 → total 4  

This makes some crossings “heavier” than others. It teaches cost-sensitive planning:
search has to consider **path cost**, not just step count. In our puzzle the optimal
**sequence** often stays the same, but the **total cost** reflects the extra effort of
moving the animals/produce.
"""
    )
