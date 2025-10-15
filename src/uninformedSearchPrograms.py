# src/uninformedSearchPrograms.py
# Uninformed search “agent programs” (BFS/DFS) returning a goal Node.

from collections import deque
from src.nodeClass import Node


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
