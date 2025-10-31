import streamlit as st
import os

# our lab modules
from data.data_lab6_task1_examCSP import make_exam_csp
from data.data_lab6_task2_asteriskSudokuCSP import make_asterisk_sudoku_csp
from src.algorithms import AC3

# pyvis stuff
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components


# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------
def show_html(path: str, height: int = 850):
    """Embed a saved HTML file (pyvis) into Streamlit, tolerant to Windows encodings."""
    if not os.path.exists(path):
        st.warning(f"{path} not found.")
        return

    # read as binary first
    with open(path, "rb") as f:
        raw = f.read()

    # try utf-8, fall back to cp1252 (Windows)
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        html = raw.decode("cp1252", errors="replace")

    import streamlit.components.v1 as components
    components.html(html, height=height, scrolling=True)

def visualize_exam_csp(csp, html_name: str, after_ac3: bool = False):
    title = "Lab 6 – Task 1: Exam Schedule" + (" (after AC-3)" if after_ac3 else " (original)")
    net = Network(
        heading=title,
        bgcolor="#222222",
        font_color="white",
        height="750px",
        width="100%",
    )
    G = nx.Graph()

    for v in csp.variables:
        dom = csp.curr_domains[v] if after_ac3 and csp.curr_domains else csp.domains[v]
        color = "yellow" if len(dom) == 1 else "white"
        G.add_node(v, color=color, title=", ".join(dom), label=v)

    for v in csp.variables:
        for n in csp.neighbors[v]:
            if (n, v) not in G.edges():
                G.add_edge(v, n, color="red")

    net.from_nx(G)
    net.toggle_physics(False)
    net.save_graph(html_name)


def visualize_asterisk_sudoku(csp, html_name: str, after_ac3: bool = False):
    ROWS = "ABCDEFGHI"
    COLS = "123456789"

    def box_id(cell):
        r = ROWS.index(cell[0]) // 3
        c = COLS.index(cell[1]) // 3
        return (r, c)

    # if you change the asterisk shape in data file, import it again
    # but we can read it off csp.neighbors(no direct list) so we keep colors simple
    net = Network(
        heading="Lab 6 – Task 2: Asterisk Sudoku" + (" (after AC-3)" if after_ac3 else " (original)"),
        bgcolor="#222222",
        font_color="white",
        height="900px",
        width="100%",
    )
    G = nx.Graph()

    cells = list(csp.variables)
    ROWS_LIST = list(ROWS)
    COLS_LIST = list(COLS)

    # get domains
    for cell in cells:
        dom = csp.curr_domains[cell] if after_ac3 and csp.curr_domains else csp.domains[cell]
        # approximate asterisk membership: if it has more neighbors than row+col+box, likely asterisk too
        # but better: color all singletons yellow, others white
        color = "yellow" if len(dom) == 1 else "white"
        # coordinates as 9x9 grid
        r = ROWS_LIST.index(cell[0])
        c = COLS_LIST.index(cell[1])
        x = (c + 1) * 60
        y = (r + 1) * 60
        G.add_node(
            cell,
            color=color,
            title=",".join(str(v) for v in dom),
            label="" if len(dom) != 1 else cell,
            x=x,
            y=y,
        )

    for c1 in cells:
        for c2 in csp.neighbors[c1]:
            if (c2, c1) in G.edges():
                continue
            # color edge types like the PDF did for simple sudoku
            if c1[0] == c2[0]:
                ec = "red"
            elif c1[1] == c2[1]:
                ec = "blue"
            elif box_id(c1) == box_id(c2):
                ec = "green"
            else:
                # this will catch the extra asterisk edges
                ec = "purple"
            G.add_edge(c1, c2, color=ec)

    net.from_nx(G)
    net.toggle_physics(False)
    net.save_graph(html_name)


# ---------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------
st.set_page_config(page_title="Lab 6 – CSP & AC-3", layout="wide")
st.title("Lab 6 – CSP, Constraint Propagation (AC-3)")

tab1, tab2 = st.tabs(
    [
        "Task 1 – Exam Schedule",
        "Task 2 – Asterisk Sudoku",
    ]
)

# ---------------------------------------------------------
# TAB 1 – EXAM SCHEDULE
# ---------------------------------------------------------
with tab1:
    st.subheader("Task 1 – Exam Schedule CSP")
    st.write("Variables: 7 courses. Domain = possible exam days. Main constraint: all different.")

    # build CSP from data file
    exam_csp = make_exam_csp()

    # visualize BEFORE
    visualize_exam_csp(exam_csp, "exams_before.html", after_ac3=False)
    st.markdown("**Original CSP (before AC-3):**")
    show_html("exams_before.html")

    # run AC-3
    AC3(exam_csp)

    # visualize AFTER
    visualize_exam_csp(exam_csp, "exams_after.html", after_ac3=True)
    st.markdown("**After AC-3:**")
    show_html("exams_after.html")

    # PDF asked specifically for these 3:
    st.markdown("**Resulting domains (what PDF asked for):**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Practical Programming Methodology")
        st.code(str(exam_csp.curr_domains["Practical Programming Methodology"]))
    with col2:
        st.write("Computer Organization and Architecture I")
        st.code(str(exam_csp.curr_domains["Computer Organization and Architecture I"]))
    with col3:
        st.write("Linear Algebra I")
        st.code(str(exam_csp.curr_domains["Linear Algebra I"]))

    # show all, just in case
    with st.expander("Show all course domains after AC-3"):
        for v in exam_csp.variables:
            st.write(f"- **{v}** → {exam_csp.curr_domains[v]}")


# ---------------------------------------------------------
# TAB 2 – ASTERISK SUDOKU
# ---------------------------------------------------------
with tab2:
    st.subheader("Task 2 – Asterisk Sudoku CSP")
    st.write(
        "9×9 Sudoku with row, column, 3×3-box constraints **plus** the extra 'asterisk' cells that must also be 1..9."
    )

    sudoku_csp = make_asterisk_sudoku_csp()

    # BEFORE
    visualize_asterisk_sudoku(sudoku_csp, "asterisk_before.html", after_ac3=False)
    st.markdown("**Original CSP (before AC-3):**")
    show_html("asterisk_before.html", height=900)

    # run AC-3
    AC3(sudoku_csp)

    # AFTER
    visualize_asterisk_sudoku(sudoku_csp, "asterisk_after.html", after_ac3=True)
    st.markdown("**After AC-3:**")
    show_html("asterisk_after.html", height=900)

    st.markdown("**All cell domains after AC-3 (PDF requirement):**")
    # print all 81 in a grid-ish way
    rows = "ABCDEFGHI"
    cols = "123456789"
    for r in rows:
        row_vals = []
        for c in cols:
            cell = r + c
            row_vals.append(f"{cell}: {sudoku_csp.curr_domains[cell]}")
        st.code(" | ".join(row_vals))
