# src/multigoal_problem_ext.py
# ---------------------------------------------------------------------
# Multi-goal Maze Problem for Lab 5 (collect all foods then reach finish).
# This is a new Problem class; it does not change your existing files.
# State = (position, frozenset(remaining_foods))
# ---------------------------------------------------------------------

from __future__ import annotations
from typing import Dict, Iterable, List, Set, Tuple, FrozenSet
from src.problemClass import Problem

Pos = Tuple[int, int]
StateMG = Tuple[Pos, FrozenSet[Pos]]

class MultiGoalMazeProblem(Problem):
    """
    - graph.origin: { pos: { action: pos2, ... }, ... }
    - Graph edge costs from graph.get(pos, pos2) (usually 1)
    Goal condition: remaining_foods == empty AND pos == finish
    """

    def __init__(self, initial_pos: Pos, finish: Pos, foods: Set[Pos], graph):
        # Encode full state
        initial_state: StateMG = (initial_pos, frozenset(foods))
        super().__init__(initial_state, finish)  # we store finish in self.goal for reference
        self.finish: Pos = finish
        self.graph = graph

    # ----- Interface required by Problem -----
    def actions(self, state: StateMG):
        pos, remaining = state
        # Same actions as in the single-goal MazeProblem: keys of graph.origin[pos]
        return list(self.graph.origin[pos].keys())

    def result(self, state: StateMG, action) -> StateMG:
        pos, remaining = state
        next_pos = self.graph.origin[pos][action]
        next_remaining = remaining
        # If we step onto a food cell, remove it from the set
        if next_pos in next_remaining:
            next_remaining = frozenset([f for f in next_remaining if f != next_pos])
        return (next_pos, next_remaining)

    def goal_test(self, state: StateMG) -> bool:
        pos, remaining = state
        return (pos == self.finish) and (len(remaining) == 0)

    def path_cost(self, cost_so_far: float, state: StateMG, action, next_state: StateMG) -> float:
        pos, remaining = state
        next_pos, _ = next_state
        step = self.graph.get(pos, next_pos)  # typically 1
        return cost_so_far + (step if step is not None else 1.0)
