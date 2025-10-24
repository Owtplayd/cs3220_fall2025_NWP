# src/PS_agentPrograms_extra.py
from search_algos import astar as _astar, ida_star as _ida
from src.heuristics import euclidean, manhattan


def A_Star_Euclidean():
    def program(problem):
        goal, stats = _astar(problem, euclidean, want_stats=True)
        print(
            f"[A* Euclidean] nodes expanded: {stats['expanded']}, path cost: {stats['cost']}"
        )
        return goal

    return program


def A_Star_Manhattan():
    def program(problem):
        goal, stats = _astar(problem, manhattan, want_stats=True)
        print(
            f"[A* Manhattan] nodes expanded: {stats['expanded']}, path cost: {stats['cost']}"
        )
        return goal

    return program


def IDAStar(use_manhattan=False):
    h = manhattan if use_manhattan else euclidean

    def program(problem):
        goal, stats = _ida(problem, h)
        print(
            f"[IDA* {'Manhattan' if use_manhattan else 'Euclidean'}] "
            f"expanded: {stats['expanded']}, cost: {stats['cost']}, thresholds: {stats['thresholds']}"
        )
        return goal

    return program
