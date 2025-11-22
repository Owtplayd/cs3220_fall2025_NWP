# ==========================================================
# run_lab7.py
# Streamlit web app for Lab 7 – Backtracking for CSPs
#   Task 1: Dinner Accommodation
#   Task 2: Asterisk Sudoku (re-using Lab 6 data file)
# ==========================================================

import streamlit as st
from pyvis.network import Network
from streamlit.components.v1 import html

from data.data_lab7_task1_dinnerCSP import (
    make_dinner_csp,
    CHAIRS,
)

from data.data_lab6_task2_asteriskSudokuCSP import (
    make_asterisk_sudoku_csp,
    ROWS,
    COLS,
    ASTERISK_CELLS,
)

from src.csp_backtracking_agentProgram import (
    run_AC3_on_csp,
    backtracking_with_trace,
)


# ----------------------------------------------------------
# Helper: build & display a PyVis graph from CSP neighbors
# ----------------------------------------------------------
def pyvis_from_neighbors(variables, neighbors, title="Constraint Graph"):
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        directed=False,
    )
    for v in variables:
        net.add_node(v, label=v)

    added_edges = set()
    for v in variables:
        for u in neighbors[v]:
            if (u, v) not in added_edges:
                net.add_edge(v, u)
                added_edges.add((v, u))

    net.set_options(
        """
        var options = {
          "physics": { "enabled": false },
          "nodes": { "shape": "dot", "size": 16 }
        }
        """
    )
    return net


def show_pyvis(net, key: str):
    """
    Save the PyVis network to an HTML file and embed it in Streamlit.
    We use write_html instead of show() to avoid notebook/template issues.
    """
    html_name = f"{key}.html"
    net.write_html(html_name)
    with open(html_name, "r", encoding="utf-8") as f:
        html(f.read(), height=620, scrolling=True)


# ----------------------------------------------------------
# Streamlit app
# ----------------------------------------------------------
def main():
    st.set_page_config(page_title="Lab 7 – Backtracking for CSPs", layout="wide")
    st.title("Lab 7 – Backtracking for CSPs")

    tab1, tab2 = st.tabs(["Task 1 – Dinner Accommodation", "Task 2 – Asterisk Sudoku"])

    # ======================================================
    # TAB 1 – Dinner Accommodation
    # ======================================================
    with tab1:
        st.header("Task 1 – The Dinner Accommodation Problem")

        st.write(
            """
            Five colleagues **A, B, C, D, E** are to be placed around a round table with
            **6 chairs** (one extra seat can be Empty).

            **Constraints:**
            * Everyone appears exactly once (plus one **Empty** seat)
            * A cannot sit next to B  
            * B cannot sit next to E  
            * B cannot sit next to C
            """
        )

        # Build CSP
        dinner_csp = make_dinner_csp()

        # --- Constraint graph ---
        if st.checkbox("Show Dinner CSP constraint graph", value=True):
            net = pyvis_from_neighbors(dinner_csp.variables, dinner_csp.neighbors)
            show_pyvis(net, key="dinner_graph")

        # --- AC-3 ---
        st.subheader("Step 1 – AC-3 (constraint propagation)")

        if st.button("Run AC-3 on Dinner CSP"):
            consistent, checks, csp_after = run_AC3_on_csp(dinner_csp)
            st.write(f"**Consistent:** `{consistent}`  |  **Checks:** `{checks}`")
            if csp_after.curr_domains is not None:
                st.write("Domains after AC-3:")
                st.json({v: csp_after.curr_domains[v] for v in csp_after.variables})
            else:
                st.info("No domains were pruned (curr_domains is None).")

        # --- Backtracking search + visualization ---
        st.subheader("Step 2 – Backtracking search")

        # Session state to keep solution & trace across reruns
        if "dinner_solution" not in st.session_state:
            st.session_state.dinner_solution = None
        if "dinner_trace" not in st.session_state:
            st.session_state.dinner_trace = None

        # When button pressed, compute once and store
        if st.button("Solve Dinner CSP with backtracking"):
            dinner_csp_bt = make_dinner_csp()
            solution, trace = backtracking_with_trace(dinner_csp_bt)
            st.session_state.dinner_solution = solution
            st.session_state.dinner_trace = trace

        solution = st.session_state.dinner_solution
        trace = st.session_state.dinner_trace

        if solution is not None and trace:
            st.success("Solution found!")

            st.write("### Final seating (Seat → Person)")
            for seat in sorted(CHAIRS, key=lambda s: int(s.replace("Seat", ""))):
                st.write(f"- **{seat}** : {solution[seat]}")

            st.markdown("---")
            st.write(f"Recorded backtracking steps: `{len(trace)}`")

            # Slider now reads from session_state and does NOT reset
            idx = st.slider(
                "Step index",
                min_value=1,
                max_value=len(trace),
                value=1,
                key="dinner_step_slider",
            )

            step = trace[idx - 1]
            st.write(
                f"Step **{step['step']}** – event: `{step['event']}`, "
                f"var: `{step['var']}`, val: `{step['val']}`"
            )
            st.json(step["assignment"])

    # ======================================================
    # TAB 2 – Asterisk Sudoku (Assignment 6)
    # ======================================================
    with tab2:
        st.header("Task 2 – Asterisk Sudoku (Assignment 6)")

        st.write(
            """
            **CSP model:**
            * Variables: 81 cells A1..I9  
            * Domains: digits 1–9 (or singleton lists for givens)  
            * Constraints:
              - all rows: all-different  
              - all columns: all-different  
              - all 3×3 boxes: all-different  
              - asterisk cells (★ set) also all-different
            """
        )

        st.write("Asterisk (★) cells:", ", ".join(ASTERISK_CELLS))

        sudoku_csp = make_asterisk_sudoku_csp()

        if st.checkbox("Show Sudoku constraint graph (dense!)"):
            net = pyvis_from_neighbors(sudoku_csp.variables, sudoku_csp.neighbors)
            show_pyvis(net, key="sudoku_graph")

        # Session state for Sudoku solution & trace
        if "sudoku_solution" not in st.session_state:
            st.session_state.sudoku_solution = None
        if "sudoku_trace" not in st.session_state:
            st.session_state.sudoku_trace = None

        if st.button("Solve Asterisk Sudoku with backtracking"):
            sudoku_csp_bt = make_asterisk_sudoku_csp()
            solution, trace = backtracking_with_trace(sudoku_csp_bt)
            st.session_state.sudoku_solution = solution
            st.session_state.sudoku_trace = trace

        solution = st.session_state.sudoku_solution
        trace = st.session_state.sudoku_trace

        if solution is not None and trace:
            st.success("Sudoku solved!")

            st.subheader("Final grid")
            for r in ROWS:
                row_vals = [str(solution[r + c]) for c in COLS]
                st.write(" ".join(row_vals))

            st.markdown("---")
            st.write(f"Recorded backtracking steps: `{len(trace)}`")

            idx = st.slider(
                "Sudoku step index",
                min_value=1,
                max_value=len(trace),
                value=1,
                key="sudoku_step_slider",
            )

            step = trace[idx - 1]
            st.write(
                f"Step **{step['step']}** – event: `{step['event']}`, "
                f"var: `{step['var']}`, val: `{step['val']}`"
            )
            st.json(step["assignment"])


if __name__ == "__main__":
    main()
