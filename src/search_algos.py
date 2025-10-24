# src/search_algos.py
from queue import PriorityQueue
from math import inf
from typing import Callable, Dict, Any
from src.nodeClass import Node


def astar(problem, h: Callable, want_stats: bool = True):
    start = Node(problem.initial)
    frontier = PriorityQueue()
    counter = 0
    frontier.put((0.0, counter, start))
    reached: Dict[Any, Node] = {start.state: start}
    expanded = 0

    while not frontier.empty():
        _, _, node = frontier.get()
        expanded += 1

        if problem.goal_test(node.state):
            stats = {"expanded": expanded, "cost": node.path_cost}
            return node, stats if want_stats else node

        for child in node.expand(problem):
            f = child.path_cost + h(child.state, problem.goal)
            old = reached.get(child.state)
            if old is None or child.path_cost < old.path_cost:
                reached[child.state] = child
                counter += 1
                frontier.put((f, counter, child))

    return None, {"expanded": expanded, "cost": float("inf")} if want_stats else None


def ida_star(problem, h: Callable):
    start = Node(problem.initial)
    start_f = h(start.state, problem.goal)
    thresholds = [start_f]
    expanded_total = 0

    def dfs_contour(node: Node, f_limit: float):
        nonlocal expanded_total
        expanded_total += 1
        f_cost = node.path_cost + h(node.state, problem.goal)
        if f_cost > f_limit:
            return None, f_cost
        if problem.goal_test(node.state):
            return node, f_cost
        next_limit = inf
        for child in node.expand(problem):
            sol, new_limit = dfs_contour(child, f_limit)
            if sol is not None:
                return sol, new_limit
            if new_limit < next_limit:
                next_limit = new_limit
        return None, next_limit

    limit = start_f
    while True:
        goal, new_limit = dfs_contour(start, limit)
        thresholds.append(new_limit)
        if goal is not None:
            return goal, {
                "expanded": expanded_total,
                "cost": goal.path_cost,
                "thresholds": thresholds,
            }
        if new_limit == inf:
            return None, {
                "expanded": expanded_total,
                "cost": float("inf"),
                "thresholds": thresholds,
            }
        limit = new_limit
