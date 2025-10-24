# PS_agentPrograms.py
# ---------------------------------------------------------------------
# Search agent programs for the Maze / Pac-Man lab.
# This file implements:
#   - A* with Euclidean heuristic
#   - A* with Manhattan heuristic
#   - IDA* (iterative deepening A*), usable for multi-goal variants
# Each solver returns (solution_path, actions, nodes_expanded, total_cost).
# The API keeps the same project structure (Problem/Node), but does not
# rely on extra methods on Node: we generate child nodes locally.
# ---------------------------------------------------------------------

from __future__ import annotations
from typing import Callable, Dict, Iterable, List, Optional, Tuple
from dataclasses import dataclass, field
import heapq
import math

# Project types
from src.problemClass import Problem
from src.nodeClass import Node

State = Tuple[int, int]  # (row, col) coordinates for maze states
Heuristic = Callable[[State], float]

# ---------- Heuristics -------------------------------------------------


def euclidean(a: State, b: State) -> float:
    """Euclidean distance (admissible for 4-neighbour grids)."""
    return math.dist(a, b)


def manhattan(a: State, b: State) -> float:
    """Manhattan distance (admissible for 4-neighbour grids)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ---------- Utilities --------------------------------------------------


def reconstruct(node: Node) -> Tuple[List[State], List]:
    """Return (states, actions) from root to this node."""
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


def expand(problem: Problem, node: Node) -> Iterable[Node]:
    """Generate child nodes from `node` using the Problem interface."""
    for a in problem.actions(node.state):
        s2 = problem.result(node.state, a)
        g2 = problem.path_cost(node.path_cost, node.state, a, s2)
        yield Node(s2, parent=node, action=a, path_cost=g2)


# ---------- A* (generic) ----------------------------------------------


def astar_search(
    problem: Problem, h_for: Callable[[State], float]
) -> Tuple[List[State], List, int, float]:
    """
    Generic A* graph search.
    Returns (path_states, path_actions, nodes_expanded, total_cost).
    """
    start = Node(problem.initial, path_cost=0, parent=None, action=None)
    frontier: List[Tuple[float, int, Node]] = []
    push_count = 0

    def f(n: Node) -> float:
        return n.path_cost + h_for(n.state)

    heapq.heappush(frontier, (f(start), push_count, start))
    push_count += 1

    # best_g[state] = best known path_cost to state
    best_g: Dict[State, float] = {start.state: 0.0}
    nodes_expanded = 0

    while frontier:
        _, _, node = heapq.heappop(frontier)

        # Goal check
        if problem.goal_test(node.state):
            states, actions = reconstruct(node)
            return states, actions, nodes_expanded, node.path_cost

        nodes_expanded += 1

        for child in expand(problem, node):
            g = child.path_cost
            if g < best_g.get(child.state, float("inf")):
                best_g[child.state] = g
                heapq.heappush(frontier, (g + h_for(child.state), push_count, child))
                push_count += 1

    # Failure
    return [], [], nodes_expanded, float("inf")


# ---------- Concrete A* variants --------------------------------------


def AStar_Euclidean(problem: Problem) -> Tuple[List[State], List, int, float]:
    """A* using Euclidean distance."""
    goal = problem.goal if not isinstance(problem.goal, list) else problem.goal[0]
    return astar_search(problem, lambda s: euclidean(s, goal))


def AStar_Manhattan(problem: Problem) -> Tuple[List[State], List, int, float]:
    """A* using Manhattan distance."""
    goal = problem.goal if not isinstance(problem.goal, list) else problem.goal[0]
    return astar_search(problem, lambda s: manhattan(s, goal))


# ---------- IDA* -------------------------------------------------------


@dataclass(order=True)
class _IDAFrame:
    f: float
    node: Node = field(compare=False)


def ida_star(
    problem: Problem, h_for: Callable[[State], float]
) -> Tuple[List[State], List, int, float]:
    """
    Iterative Deepening A* (IDA*).
    Returns (path_states, path_actions, nodes_expanded, total_cost).
    """
    start = Node(problem.initial, path_cost=0, parent=None, action=None)
    bound = h_for(start.state)
    nodes_expanded = 0

    def search(node: Node, g: float, bound: float) -> Tuple[Optional[Node], float, int]:
        """Depth-first search bounded by f <= bound. Returns (goal_node, next_bound, expanded_count)."""
        nonlocal nodes_expanded
        f = g + h_for(node.state)
        if f > bound:
            return None, f, 0
        if problem.goal_test(node.state):
            return node, bound, 0
        min_excess = float("inf")
        expanded_here = 0
        for child in expand(problem, node):
            nodes_expanded += 1
            expanded_here += 1
            goal_node, t, _ = search(child, child.path_cost, bound)
            if goal_node is not None:
                return goal_node, bound, expanded_here
            if t < min_excess:
                min_excess = t
        return None, min_excess, expanded_here

    while True:
        goal_node, t, _ = search(start, 0.0, bound)
        if goal_node is not None:
            states, actions = reconstruct(goal_node)
            return states, actions, nodes_expanded, goal_node.path_cost
        if t == float("inf"):
            return [], [], nodes_expanded, float("inf")
        bound = t


# ---------- Multi-goal helper (nearest-food-first) ---------------------


def make_multigoal_heuristic(foods: List[State], final_goal: State) -> Heuristic:
    """
    Admissible heuristic for 'collect all foods, then go to final_goal'.
    We take the distance to the nearest remaining food using Manhattan (admissible),
    plus 0 for the rest (a light under-estimate). Once no foods remain, use
    distance to final_goal.
    """
    foods_set = set(foods)

    def h(state: State) -> float:
        if foods_set:
            return min(manhattan(state, f) for f in foods_set)
        else:
            return manhattan(state, final_goal)

    return h


# ---------- High-level wrappers expected by the project ----------------


def A_StarSearchAgentProgram(
    h_func: Callable[[State], float],
) -> Callable[[Problem], Tuple[List[State], List, int, float]]:
    """
    Adapter to keep the 'agent program' style used in the project:
    returns a function that, when given a Problem, runs A* with the provided
    heuristic and returns (states, actions, nodes_expanded, total_cost).
    """

    def program(problem: Problem):
        return astar_search(problem, h_func)

    return program


def ProblemSolvingMazeAgentAstar_Euclidean(problem: Problem):
    return AStar_Euclidean(problem)


def ProblemSolvingMazeAgentAstar_Manhattan(problem: Problem):
    return AStar_Manhattan(problem)


def IDAStar_AgentProgram(
    h_func: Callable[[State], float],
) -> Callable[[Problem], Tuple[List[State], List, int, float]]:
    def program(problem: Problem):
        return ida_star(problem, h_func)

    return program
