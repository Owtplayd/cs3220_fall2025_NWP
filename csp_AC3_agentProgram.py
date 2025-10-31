# ==========================================================
# csp_AC3_agentProgram.py
# Generic CSP agent for Lab 6
# =========================================================P

from src.algorithms import AC3

try:
    from pyvis.network import Network
    import networkx as nx
    HAS_PYVIS = True
except ImportError:
    HAS_PYVIS = False

def run_AC3_on_csp(csp, make_html=False, html_prefix="csp"):
    if make_html and not HAS_PYVIS:
        print("pyvis/networkx not installed – skipping visualization.")

    # before
    if make_html and HAS_PYVIS:
        _visualize_csp(csp, f"{html_prefix}_before.html", after_ac3=False)

    print("=== Running AC-3 on CSP ===")
    AC3(csp)
    print("=== AC-3 finished ===")

    # after
    if make_html and HAS_PYVIS:
        _visualize_csp(csp, f"{html_prefix}_after.html", after_ac3=True)

    print("\n--- Domains after AC-3 ---")
    for v in csp.variables:
        print(f"{v}: {csp.curr_domains[v]}")

def _visualize_csp(csp, html_name, after_ac3=False):
    if not HAS_PYVIS:
        return

    net = Network(
        heading=f"Lab 6 CSP – {'after AC-3' if after_ac3 else 'original'}",
        bgcolor="#242020",
        font_color="white",
        height="750px",
        width="100%"
    )

    G = nx.Graph()

    for v in csp.variables:
        dom = csp.curr_domains[v] if after_ac3 and csp.curr_domains else csp.domains[v]
        color = "yellow" if len(dom) == 1 else "white"
        G.add_node(v, color=color, title=", ".join(str(x) for x in dom), label=v)

    for v in csp.variables:
        for nb in csp.neighbors[v]:
            if (nb, v) not in G.edges():
                G.add_edge(v, nb, color="red")

    net.from_nx(G)
    net.toggle_physics(False)
    net.save_graph(html_name)
    print(f"✅ saved {html_name}")
