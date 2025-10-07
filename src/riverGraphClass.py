# src/riverGraphClass.py
from collections import deque
from pyvis.network import Network
from src.riverProblemClass import RiverProblem


class RiverStateSpace:
    """Builds the legal state-space graph and provides PyVis export."""

    def __init__(self, problem: RiverProblem):
        self.problem = problem
        self.nodes = set()
        self.edges = []  # (from_state, to_state, action)

    def build(self):
        q = deque([self.problem.initial])
        seen = {self.problem.initial}
        self.nodes.add(self.problem.initial)

        while q:
            s = q.popleft()
            for a in self.problem.actions(s):
                ns = self.problem.result(s, a)
                if ns is None:
                    continue
                self.edges.append((s, ns, a))
                if ns not in seen:
                    seen.add(ns)
                    self.nodes.add(ns)
                    q.append(ns)
        return self

    def to_pyvis(self, html_path="wgc_state_space.html"):
        # Follow your course HTML look (dark bg, labels, arrows). See graph1/graph2. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}
        net = Network(
            height="750px",
            width="100%",
            bgcolor="#242020",
            font_color="white",
            directed=True,
        )
        net.barnes_hut()

        for s in self.nodes:
            label = f"F{s[0]} W{s[1]} G{s[2]} C{s[3]}"
            color = (
                "red"
                if s == self.problem.initial
                else "green" if self.problem.goal_test(s) else "#97c2fc"
            )
            net.add_node(str(s), label=label, title=str(s), color=color, shape="dot")

        for u, v, a in self.edges:
            net.add_edge(str(u), str(v), label=a, arrows="to")

        net.show(html_path)
        return html_path
