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
        st.write("**States along path:**")
        for i, n in enumerate(nodes):
            act = f"  ← {n.action}" if i > 0 else ""
            st.write(f"Step {i}: {n.state}{act}   (g={n.path_cost})")
        st.success(f"Plan: {actions}")
        st.info(f"Total cost: {total_cost}")
    else:
        st.warning(
            "Could not interpret the return shape from BestFirstSearchAgentProgram."
        )
        st.write("Raw object returned by program:", sol)
