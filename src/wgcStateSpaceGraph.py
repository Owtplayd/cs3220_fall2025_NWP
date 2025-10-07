# src/wgcStateSpaceGraph.py
from collections import deque
from pyvis.network import Network
from src.wgcProblemClass import WGCProblem


def state_label(s):
    f, w, g, c = s
    return f"F:{f} W:{w} G:{g} C:{c}"


def build_state_space_html(filename="graph_wgc.html", cost_mode="v1"):
    """
    Build the reachable state-space from the initial state using BFS and
    write a standalone HTML with PyVis. We use write_html() instead of show()
    to avoid the Jupyter-notebook template path that can trigger a NoneType
    .render() error in some setups.
    """
    problem = WGCProblem(cost_mode=cost_mode)
    start = problem.initial

    net = Network(height="750px", width="100%", bgcolor="#242020")
    net.toggle_physics(True)

    # add start node
    net.add_node(state_label(start), label=state_label(start), color="red")

    seen = {start}
    q = deque([start])

    # to speed node existence checks, keep a set of added node ids
    added_ids = {state_label(start)}

    while q:
        s = q.popleft()
        for a in problem.actions(s):
            ns = problem.result(s, a)
            nid = state_label(ns)

            if nid not in added_ids:
                color = "green" if problem.goal_test(ns) else "#97c2fc"
                net.add_node(nid, label=nid, color=color)
                added_ids.add(nid)

            net.add_edge(state_label(s), nid, label=a, arrows="to")

            if ns not in seen:
                seen.add(ns)
                q.append(ns)

    # IMPORTANT: write_html instead of show()
    net.write_html(filename, open_browser=False)
    return filename


if __name__ == "__main__":
    build_state_space_html()
