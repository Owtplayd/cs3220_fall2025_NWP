# lab3app_maze.py
# Streamlit app for Task 2: Treasure Maze (with narration + plan preview)
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx

from src.graphClass import Graph
from src.treasureMazeEnvironmentClass import TreasureMazeEnvironment
from src.treasureMazeAgentClass import TreasureMazeAgent
from src.PS_agentPrograms import BestFirstSearchAgentProgram
from data.TreasureMazeData import mazeData, MAZE_START, MAZE_EXIT

st.set_page_config(page_title="Treasure Maze — Problem-Solving Agent", layout="wide")


# -------------------- helpers --------------------
def _edge_key(u, v):
    # normalize undirected edge key
    return tuple(sorted((u, v)))


def _pairwise(seq):
    for i in range(len(seq) - 1):
        yield seq[i], seq[i + 1]


def build_graph_html(
    graph_data,
    start,
    exit_node,
    treasures,
    agent_loc=None,
    trail_edges=None,
    plan_edges=None,
):
    """Render the maze with PyVis.
    - trail_edges: thick orange (traversed)
    - plan_edges : dashed cyan (planned next moves)"""
    trail_edges = trail_edges or set()
    plan_edges = plan_edges or set()

    g = nx.Graph()
    for a, nbrs in graph_data.items():
        g.add_node(a)
        for b, w in nbrs.items():
            g.add_edge(a, b, label=str(w))

    net = Network(
        height="750px",
        width="100%",
        bgcolor="#242020",
        font_color="white",
        directed=False,
    )

    # nodes
    for n in g.nodes():
        label = n
        color = "#97c2fc"  # default
        if n == start:
            color = "red"
        if n == exit_node:
            color = "green"
        if n in treasures:
            label = f"{n} {treasures[n]}"
        if agent_loc == n:
            color = "orange"
        net.add_node(n, label=label, title=n, color=color, shape="dot")

    # edges (priority: trail > plan > normal)
    for u, v, d in g.edges(data=True):
        key = _edge_key(u, v)
        if key in trail_edges:
            net.add_edge(u, v, label=d.get("label", ""), width=4, color="orange")
        elif key in plan_edges:
            net.add_edge(
                u, v, label=d.get("label", ""), dashes=True, color="cyan", width=2
            )
        else:
            net.add_edge(u, v, label=d.get("label", ""))

    tmp_path = "/tmp/treasure_maze_graph.html"
    net.write_html(tmp_path, open_browser=False)
    return open(tmp_path, "r", encoding="utf-8").read()


def render_env(env, agent, trail_edges, plan_edges):
    st.header("State of the Environment:", divider="red")
    html = build_graph_html(
        env.status.graph_dict,
        env.start_node,
        env.exit_node,
        env.treasures,
        agent_loc=agent.state,
        trail_edges=trail_edges,
        plan_edges=plan_edges,
    )
    components.html(html, height=800, scrolling=True)

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"Agent now at : **{agent.state}**.")
        st.info(f"Current Agent performance {agent.performance}")
    with c2:
        if agent.treasure_picked:
            st.success(f"Treasure collected: {agent.treasure_picked}")
        goal_txt = (
            "Pick any treasure"
            if not agent.have_treasure
            else f"Head to exit **{env.exit_node}**"
        )
        st.success(goal_txt)

    # Show planned node sequence as text (readability for instructor)
    planned_nodes = [agent.state] + list(agent.seq)
    if len(planned_nodes) > 1:
        preview = " → ".join(planned_nodes[:12])
        if len(planned_nodes) > 12:
            preview += " → …"
        st.caption(f"Planned path preview: {preview}")
    else:
        st.caption("Planned path preview: (none)")


def _append_log(msg):
    st.session_state.log.append(msg)


# -------------------- app --------------------
def main():
    st.title("Resolving Treasure Maze Problem ...")

    # ---- first load: build env & agent ----
    if "env" not in st.session_state:
        maze_graph = Graph(mazeData)
        env = TreasureMazeEnvironment(
            maze_graph, MAZE_START, MAZE_EXIT
        )  # random treasures each run
        agent = TreasureMazeAgent(
            initial_state=MAZE_START,
            dataGraph=maze_graph,
            exit_node=MAZE_EXIT,
            treasures=env.treasures,
            program=BestFirstSearchAgentProgram(),
        )
        env.add_thing(agent)  # primes initial plan

        st.session_state.env = env
        st.session_state.agent = agent
        st.session_state.trail_edges = set()  # set of normalized edge tuples
        st.session_state.last_node = agent.state
        st.session_state.log = []
        st.session_state.step_no = 0
        _append_log(f"Start at {agent.state}; initial performance {agent.performance}.")

    env = st.session_state.env
    agent = st.session_state.agent
    trail_edges = st.session_state.trail_edges

    # ---- compute current plan edges for overlay ----
    plan_nodes = [agent.state] + list(agent.seq)
    plan_edges = (
        {_edge_key(u, v) for (u, v) in _pairwise(plan_nodes)}
        if len(plan_nodes) > 1
        else set()
    )

    # ---- finished? ----
    if env.is_done():
        render_env(env, agent, trail_edges, plan_edges=set())  # no plan when finished
        if agent.have_treasure and agent.state == env.exit_node:
            st.success(
                f"Finished! Agent reached the exit at **{env.exit_node}** with treasure {agent.treasure_picked}."
            )
            _append_log(
                f"Reached exit {env.exit_node} with {agent.treasure_picked}. Final performance {agent.performance}."
            )
        else:
            st.warning("Agent stopped.")
            _append_log(
                f"Agent stopped at {agent.state}. Final performance {agent.performance}."
            )
        st.button("Reset", key="reset_btn", on_click=lambda: st.session_state.clear())

        with st.expander("Narration log", expanded=True):
            for line in st.session_state.log:
                st.write("• " + line)
        return

    # ---- normal render ----
    render_env(env, agent, trail_edges, plan_edges)

    # Single button, single render per run. On click: step then rerun.
    if st.button("Run One Agent's Step", key="step_btn"):
        st.session_state.step_no += 1
        prev = agent.state
        had_treasure_before = agent.have_treasure
        perf_before = agent.performance

        env.step()  # consumes one planned action, updates agent.state/perf

        new = agent.state
        perf_drop = perf_before - agent.performance
        if prev != new:
            trail_edges.add(_edge_key(prev, new))

        # If treasure was just picked this step, announce and replan immediately for clearer preview
        if (not had_treasure_before) and agent.have_treasure:
            _append_log(
                f"Step {st.session_state.step_no}: move {prev} → {new} (-{perf_drop}); "
                f"picked {agent.treasure_picked}; re-defining goal to exit {env.exit_node}."
            )
            agent.replan()  # update plan now so preview/overlay reflects new goal
        else:
            _append_log(
                f"Step {st.session_state.step_no}: move {prev} → {new} (-{perf_drop})."
            )

        st.session_state.last_node = new
        st.rerun()  # re-render with updated state

    # ---- narration drawer ----
    with st.expander("Narration log", expanded=False):
        for line in st.session_state.log:
            st.write("• " + line)


if __name__ == "__main__":
    main()
