# src/informed_search_ext.py
# ---------------------------------------------------------------------
# Informed search algorithms and multi-goal heuristics for Lab 5.
# No imports from any heuristics module; heuristics are defined here.
# ---------------------------------------------------------------------

from __future__ import annotations
from typing import Callable, Dict, Iterable, List, Tuple
from dataclasses import dataclass, field
import heapq
import math

from src.problemClass import Problem
from src.nodeClass import Node

State = Tuple[int, int]  # (row, col)

# ============================== Heuristics ==============================


def euclidean(a: State, b: State) -> float:
    return math.dist(a, b)


def manhattan(a: State, b: State) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================== Utilities ===============================


def _reconstruct(node: Node) -> Tuple[List[State], List]:
    states: List[State] = []
    actions: List = []
    n = node
    while n is not None:
        states.append(n.state)
        actions.append(n.action)
        n = n.parent
    states.reverse()
    actions.reverse()
    if actions and actions[0] is None:
        actions = actions[1:]
    return states, actions


def _expand(problem: Problem, node: Node) -> Iterable[Node]:
    for a in problem.actions(node.state):
        s2 = problem.result(node.state, a)
        g2 = problem.path_cost(node.path_cost, node.state, a, s2)
        yield Node(s2, parent=node, action=a, path_cost=g2)


def _on_path(node: Node, state: State) -> bool:
    n = node
    while n is not None:
        if n.state == state:
            return True
        n = n.parent
    return False


# ============================ A* (generic) ==============================


def astar_search(
    problem: Problem, h: Callable[[State], float]
) -> Tuple[List[State], List, int, float]:
    """Generic A*. Returns (path_states, path_actions, nodes_expanded, total_cost)."""
    start = Node(problem.initial, path_cost=0, parent=None, action=None)
    nodes_expanded = 0

    def f(n: Node) -> float:
        return n.path_cost + h(n.state)

    frontier: List[Tuple[float, int, Node]] = []
    push_id = 0
    heapq.heappush(frontier, (f(start), push_id, start))
    push_id += 1

    best_g: Dict[State, float] = {start.state: 0.0}

    while frontier:
        _, _, node = heapq.heappop(frontier)
        if problem.goal_test(node.state):
            states, actions = _reconstruct(node)
            return states, actions, nodes_expanded, node.path_cost

        nodes_expanded += 1

        for child in _expand(problem, node):
            g = child.path_cost
            if g < best_g.get(child.state, float("inf")):
                best_g[child.state] = g
                heapq.heappush(frontier, (g + h(child.state), push_id, child))
                push_id += 1

    return [], [], nodes_expanded, float("inf")


# ========================= A* concrete variants ========================


def astar_euclidean(problem: Problem) -> Tuple[List[State], List, int, float]:
    goal = problem.goal if not isinstance(problem.goal, list) else problem.goal[0]
    return astar_search(problem, lambda s: euclidean(s, goal))


def astar_manhattan(problem: Problem) -> Tuple[List[State], List, int, float]:
    goal = problem.goal if not isinstance(problem.goal, list) else problem.goal[0]
    return astar_search(problem, lambda s: manhattan(s, goal))


# ================================ IDA* ==================================


@dataclass(order=True)
class _IDAFrame:
    f: float
    node: Node = field(compare=False)


def ida_star(
    problem: Problem, h: Callable[[State], float]
) -> Tuple[List[State], List, int, float]:
    """IDA*. Returns (states, actions, nodes_expanded, total_cost)."""
    start = Node(problem.initial, path_cost=0, parent=None, action=None)
    bound = h(start.state)
    nodes_expanded = 0

    def search(node: Node, g: float, bound: float):
        nonlocal nodes_expanded
        f = g + h(node.state)
        if f > bound:
            return None, f
        if problem.goal_test(node.state):
            return node, f
        min_next = float("inf")
        for child in _expand(problem, node):
            # Path-based cycle pruning (prevents recursion blow-ups)
            if _on_path(node, child.state):
                continue
            nodes_expanded += 1
            found, t = search(child, child.path_cost, bound)
            if found is not None:
                return found, t
            if t < min_next:
                min_next = t
        return None, min_next

    while True:
        found, t = search(start, 0.0, bound)
        if found is not None:
            states, actions = _reconstruct(found)
            return states, actions, nodes_expanded, found.path_cost
        if t == float("inf"):
            return [], [], nodes_expanded, float("inf")
        bound = t


# ========================== Multi-goal heuristics =======================


def make_multigoal_heuristic(
    foods: List[State], final_goal: State
) -> Callable[[State], float]:
    """
    Admissible lower bound: distance to nearest remaining food (Manhattan),
    or if none remain, distance to final_goal.
    """
    foods_set = set(foods)

    def h(state: State) -> float:
        if foods_set:
            return min(manhattan(state, f) for f in foods_set)
        return manhattan(state, final_goal)

    return h


def mst_lower_bound(points: List[State]) -> float:
    """MST over points using Manhattan distance (admissible LB)."""
    if not points:
        return 0.0

    parent = {i: i for i in range(len(points))}
    rank = {i: 0 for i in range(len(points))}

    def find(i):
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri == rj:
            return False
        if rank[ri] < rank[rj]:
            parent[ri] = rj
        elif rank[ri] > rank[rj]:
            parent[rj] = ri
        else:
            parent[rj] = ri
            rank[ri] += 1
        return True

    edges = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = manhattan(points[i], points[j])
            edges.append((d, i, j))
    edges.sort(key=lambda x: x[0])

    cost = 0.0
    for d, i, j in edges:
        if union(i, j):
            cost += d
    return cost


def make_multigoal_heuristic_mst(
    foods: List[State], final_goal: State
) -> Callable[[State], float]:
    """nearest-food + MST(foods) lower bound (tighter, still admissible)."""
    foods_list = list(foods)

    def h(state: State) -> float:
        if foods_list:
            d0 = min(manhattan(state, f) for f in foods_list)
            d_mst = mst_lower_bound(foods_list) if len(foods_list) > 1 else 0.0
            return d0 + d_mst
        return manhattan(state, final_goal)

    return h
