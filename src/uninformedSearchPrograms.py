# src/uninformedSearchPrograms.py
# Uninformed search “agent programs” (BFS/DFS) returning a goal Node.

from collections import deque
from typing import Optional
from src.nodeClass import Node
import heapq


def UniformCostSearchAgentProgram():
    """
    Uniform-cost Search (Best-First with PATH-COST as priority).
    Assumes problem.path_cost accumulates non-uniform edge costs.
    """

    def program(problem):
        start = Node(problem.initial)
        if problem.goal_test(start.state):
            return start

        # (priority, tie, Node)
        frontier = []
        tie = 0
        heapq.heappush(frontier, (0, tie, start))
        reached = {problem.initial: 0}  # state -> best cost discovered

        while frontier:
            cost, _, node = heapq.heappop(frontier)
            # Early goal check when popped (optimal)
            if problem.goal_test(node.state):
                return node
            for action in problem.actions(node.state):
                child_state = problem.result(node.state, action)
                child_cost = problem.path_cost(
                    node.path_cost, node.state, action, child_state
                )
                if child_state not in reached or child_cost < reached[child_state]:
                    child = Node(
                        child_state, parent=node, action=action, path_cost=child_cost
                    )
                    reached[child_state] = child_cost
                    tie += 1
                    heapq.heappush(frontier, (child_cost, tie, child))
        return None

    return program


# ----- Iterative Deepening Search (IDS) -----
_CUTOFF = object()  # sentinel


def IDSearchAgentProgram(max_depth: int = 9999):
    """
    Iterative Deepening Search per the pseudocode in your screenshot.
    Depth-limited DFS that increases the limit from 0..max_depth.
    Returns goal Node or None if not found.
    """

    def program(problem):
        for limit in range(0, max_depth + 1):
            result = _recursive_dls(Node(problem.initial), problem, limit)
            if result is _CUTOFF:
                continue
            return result  # Node or None
        return None

    return program


def _recursive_dls(node: Node, problem, limit: int):
    if problem.goal_test(node.state):
        return node
    elif limit == 0:
        return _CUTOFF
    else:
        cutoff_occurred = False
        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            child = Node(
                child_state,
                parent=node,
                action=action,
                path_cost=problem.path_cost(
                    node.path_cost, node.state, action, child_state
                ),
            )
            result = _recursive_dls(child, problem, limit - 1)
            if result is _CUTOFF:
                cutoff_occurred = True
            elif result is not None:
                return result
        return _CUTOFF if cutoff_occurred else None


def BreadthFirstSearchAgentProgram():
    """Graph-search BFS with reached set."""

    def program(problem):
        start = Node(problem.initial)
        if problem.goal_test(start.state):
            return start

        frontier = deque([start])  # FIFO
        reached = {problem.initial: start}  # state -> Node

        while frontier:
            node = frontier.popleft()
            for action in problem.actions(node.state):
                child_state = problem.result(node.state, action)
                if child_state not in reached:
                    child = Node(
                        child_state,
                        parent=node,
                        action=action,
                        path_cost=problem.path_cost(
                            node.path_cost, node.state, action, child_state
                        ),
                    )
                    if problem.goal_test(child.state):
                        return child
                    reached[child_state] = child
                    frontier.append(child)
        return None

    return program


def DepthFirstSearchAgentProgram():
    """Graph-search DFS with reached set."""

    def program(problem):
        start = Node(problem.initial)
        if problem.goal_test(start.state):
            return start

        frontier = [start]  # LIFO
        reached = {problem.initial: start}

        while frontier:
            node = frontier.pop()
            for action in problem.actions(node.state):
                child_state = problem.result(node.state, action)
                if child_state not in reached:
                    child = Node(
                        child_state,
                        parent=node,
                        action=action,
                        path_cost=problem.path_cost(
                            node.path_cost, node.state, action, child_state
                        ),
                    )
                    if problem.goal_test(child.state):
                        return child
                    reached[child_state] = child
                    frontier.append(child)
        return None

    return program
